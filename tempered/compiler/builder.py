from .. import ast_utils
from ..parser import template_ast
from ..parser.template_ast import (
    Template, LayoutTemplate, TemplateTag,
    LiteralTag, ExprTag, HtmlTag,
    ComponentTag, StyleTag, SlotTag,
    IfTag, ForTag, BlockTag, AssignmentTag,
)
from .utils import (
    create_escape_call, slot_variable_name, slot_parameter,
    WITH_STYLES_PARAMETER, COMPONENT_CSS_VARIABLE, KWARGS_VARIABLE,
)
from .accumulators import StringVariable, ExprBuffer
import ast
import sys
import typing_extensions as t
from dataclasses import dataclass, field


@dataclass
class CodeBuilder:
    variable: StringVariable
    template: Template
    layout: t.Union[LayoutTemplate, None]
    css: t.Union[str, None]
    body: t.List[ast.stmt] = field(default_factory=list)
    buffer: ExprBuffer = field(default_factory=ExprBuffer)

    def add_expr(self, value: ast.expr):
        self.buffer.add(value)

    def enter_block(self):
        self.ensure_assigned()
        self.flush_expressions()

    def flush_expressions(self):
        expr = self.buffer.flush()
        if expr:
            self.body.append(self.variable.create_add(expr))

    def ensure_assigned(self):
        self.body.extend(self.variable.ensure_assigned())

    def construct_tag(self, tag: TemplateTag):
        if isinstance(tag, LiteralTag):
            self.add_expr(ast_utils.Constant(tag.body))
        elif isinstance(tag, ExprTag):
            self.add_expr(create_escape_call(value=tag.value))
        elif isinstance(tag, HtmlTag):
            self.add_expr(tag.value)
        elif isinstance(tag, ComponentTag):
            self.construct_component_tag(tag)
        elif isinstance(tag, BlockTag):
            self.construct_block_tag(tag)
        elif isinstance(tag, IfTag):
            self.construct_if(tag)
        elif isinstance(tag, ForTag):
            self.construct_for(tag)
        elif isinstance(tag, AssignmentTag):
            self.construct_assignment(tag)
        elif isinstance(tag, StyleTag) and self.layout is None:
            self.construct_style(tag)
        elif isinstance(tag, StyleTag):
            pass
        elif isinstance(tag, SlotTag):
            self.construct_slot_tag(tag)
        else:
            t.assert_never(tag)

    def create_block(self, tags: t.Sequence[TemplateTag]) -> t.Sequence[ast.stmt]:
        if not self.buffer.empty():
            raise RuntimeError(
                "Internal Error, must flush buffer before creating block"
            )

        ctx_block = self.create_subcontext(self.variable.variable.id + "_block")
        for tag in tags:
            ctx_block.construct_tag(tag)

        if ctx_block.variable.assigned:
            ctx_block.flush_expressions()
            expr = ctx_block.variable.variable
        else:
            expr = ctx_block.buffer.flush() or ast_utils.EmptyStr

        ctx_block.body.append(self.variable.create_add(expr))

        return ctx_block.body

    def create_variable(
        self,
        name: t.Union[str, ast.Name],
        tags: t.Sequence[TemplateTag],
    ) -> t.List[ast.stmt]:
        ctx_assign = self.create_subcontext(name)
        for tag in tags:
            ctx_assign.construct_tag(tag)

        ctx_assign.flush_expressions()
        ctx_assign.ensure_assigned()
        return ctx_assign.body

    def construct_component_tag(self, tag: ComponentTag):
        func = ast_utils.Name(tag.component_name)
        keywords = tag.keywords.copy()
        keywords[WITH_STYLES_PARAMETER] = ast_utils.Constant(False)

        func_call = ast_utils.Call(
            func=func,
            keywords=keywords,
            kwargs=ast_utils.Name(KWARGS_VARIABLE),
        )
        self.add_expr(func_call)

    def construct_assignment(self, tag: AssignmentTag):
        self.flush_expressions()
        self.body.append(
            ast_utils.Assign(
                target=tag.target,
                value=tag.value,
            )
        )

    def construct_style(self, tag: StyleTag):
        if self.css is None and not self.template.is_layout:
            return

        self.flush_expressions()
        self.ensure_assigned()

        condition = ast_utils.And(
            ast_utils.Name(WITH_STYLES_PARAMETER),
            ast_utils.Name(COMPONENT_CSS_VARIABLE),
        )
        if_body = [
            ast_utils.AddAssign(
                target=self.variable.variable,
                value=ast_utils.FormatString(
                    ast_utils.Constant("<style>"),
                    ast_utils.Name(COMPONENT_CSS_VARIABLE),
                    ast_utils.Constant("</style>"),
                ),
            )
        ]
        self.body.append(
            ast_utils.If(
                condition=condition,
                if_body=if_body,
            ),
        )

    def construct_if(self, block: IfTag):
        self.enter_block()

        if_body = self.create_block(block.if_block)

        elif_blocks: t.List[t.Tuple[ast.expr, t.Sequence[ast.stmt]]] = []
        for condition, elif_block in block.elif_blocks:
            elif_body = self.create_block(elif_block)
            elif_blocks.append((condition, elif_body))

        if block.else_block:
            else_body = self.create_block(block.else_block)
        else:
            else_body = None

        self.body.append(
            ast_utils.If(
                condition=block.condition,
                if_body=if_body,
                elif_blocks=elif_blocks,
                else_body=else_body,
            )
        )

    def construct_for(self, tag: ForTag):
        self.enter_block()

        ctx_for = self.create_subcontext(self.variable.variable.id + "_block")
        for tag_ in tag.loop_block:
            ctx_for.construct_tag(tag_)

        has_expr = not ctx_for.buffer.empty()
        is_single_expr = has_expr and len(ctx_for.body) == 0
        if is_single_expr and sys.version_info >= (3, 12):  # python3.12 comprehensions are faster
            loop_expr = ctx_for.buffer.flush()
            if loop_expr:
                generator = ast_utils.GeneratorExp(
                    expr=loop_expr,
                    loop_var=tag.loop_variable,
                    iterable=tag.iterable,
                )
                self.add_expr(ast_utils.ArrayJoin(generator))
        elif len(ctx_for.body) >= 1 or has_expr:
            for_body = self.create_block(tag.loop_block)
            self.body.append(
                ast.For(
                    target=tag.loop_variable,
                    iter=tag.iterable,
                    body=for_body,
                    orelse=[],
                )
            )

    def construct_block_tag(self, block: template_ast.BlockTag):
        self.body.extend(
            self.create_variable(
                name=slot_variable_name(block.name),
                tags=block.body,
            )
        )

    def construct_slot_tag(self, tag: SlotTag):
        slot_param = ast_utils.Name(slot_parameter(tag.name))

        if tag.default is None:
            self.add_expr(slot_param)
            return

        if_stmt = ast_utils.If(
            condition=ast_utils.Is(slot_param, ast_utils.None_),
            if_body=self.create_variable(
                name=slot_param,
                tags=tag.default,
            ),
        )
        self.body.append(if_stmt)
        self.buffer.add(slot_param)

    def create_subcontext(self, name: t.Union[str, ast.Name, None] = None):
        if name is None:
            variable = self.variable
        else:
            variable = StringVariable(name)

        return CodeBuilder(
            variable=variable, template=self.template, layout=self.layout, css=self.css
        )
