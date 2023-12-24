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
    WITH_STYLES_PARAMETER, CSS_VARIABLE, KWARGS_VARIABLE,
)
from .accumulators import Variable
import ast
import sys
import typing_extensions as t
from dataclasses import dataclass, field

USE_EXPR_BUFFER = True

@dataclass
class CodeBuilder:
    variable: Variable
    template: Template
    layout: t.Union[LayoutTemplate, None]
    css: t.Union[str, None]
    body: t.List[ast.stmt] = field(default_factory=list)

    @property
    def uses_layout(self):
        return self.layout is not None

    @property
    def is_layout(self):
        return self.template.is_layout

    def add_expr(self, expr: ast.expr):
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
        elif isinstance(tag, StyleTag) and self.uses_layout:
            # Templates that use layouts won't have their styles placed their
            pass
        elif isinstance(tag, StyleTag):
            self.construct_style(tag)
        elif isinstance(tag, SlotTag):
            self.construct_slot_tag(tag)
        else:
            t.assert_never(tag)

    def create_block(self, tags: t.Sequence[TemplateTag]) -> t.Sequence[ast.stmt]:
        ctx_block = self.create_subcontext()
        for tag in tags:
            ctx_block.construct_tag(tag)

        return ctx_block.body

    def create_variable(
        self,
        name: t.Union[str, ast.Name],
        tags: t.Sequence[TemplateTag],
    ) -> t.List[ast.stmt]:
        ctx_assign = self.create_subcontext(name)
        for tag in tags:
            ctx_assign.construct_tag(tag)
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
        self.body.append(
            ast_utils.Assign(
                target=tag.target,
                value=tag.value,
            )
        )


    def construct_if(self, block: IfTag):
        self.ensure_assigned()

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
        self.ensure_assigned()

        for_body = self.create_block(tag.loop_block)
        if len(for_body) >= 1:
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
        self.add_expr(slot_param)

    def create_subcontext(self, name: t.Union[str, ast.Name, None] = None):
        if name is None:
            variable = self.variable
        else:
            variable = Variable(name)

        return CodeBuilder(
            variable=variable, template=self.template, layout=self.layout, css=self.css
        )

    def construct_style(self, tag: StyleTag):
        if self.css is None and not self.is_layout:
            return

        self.ensure_assigned()
        if not self.is_layout:
            self.body.append(ast_utils.If(
                condition=ast_utils.Name(WITH_STYLES_PARAMETER),
                if_body=ast_utils.AddAssign(
                    target=self.variable.name,
                    value=ast_utils.Constant(f"<style>{self.css}</style>"),
                ),
            ))
        else:
            condition = ast_utils.And(
                ast_utils.Name(WITH_STYLES_PARAMETER),
                ast_utils.Name(CSS_VARIABLE),
            )
            if_body = ast_utils.AddAssign(
                target=self.variable.name,
                value=ast_utils.FormatString(
                    ast_utils.Constant("<style>"),
                    ast_utils.Name(CSS_VARIABLE),
                    ast_utils.Constant("</style>"),
                ),
            )
            self.body.append(
                ast_utils.If(
                    condition=condition,
                    if_body=[if_body],
                ),
            )
