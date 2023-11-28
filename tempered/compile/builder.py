from .. import ast_utils
from ..parser import parse_ast
from ..parser.parse_ast import (
    Template,
    LayoutTemplate,
    TemplateTag,
    LiteralTag,
    ExprTag,
    HtmlTag,
    ComponentTag,
    StyleTag,
    SlotTag,
    IfTag,
    ForTag,
    AssignmentTag,
)
from .utils import (
    create_escape_call,
    slot_variable_name,
    slot_parameter,
    WITH_STYLES_PARAMETER,
    COMPONENT_CSS_VARIABLE,
    KWARGS_VARIABLE,
)
from .accumulators import StringVariable, ExprBuffer
from copy import copy
import ast
from typing_extensions import Sequence, assert_never, Generator
from dataclasses import dataclass, field


@dataclass
class CodeBuilder:
    variable: StringVariable
    template: Template
    layout: LayoutTemplate | None
    css: str|None
    body: list[ast.stmt] = field(default_factory=list)
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
        match tag:
            case LiteralTag():
                self.add_expr(ast_utils.Constant(tag.body))
            case ExprTag():
                self.add_expr(create_escape_call(tag.value))
            case HtmlTag():
                self.add_expr(tag.value)
            case ComponentTag():
                self.construct_component_tag(tag)
            case parse_ast.BlockTag():
                self.construct_block_tag(tag)
            case IfTag():
                self.construct_if(tag)
            case ForTag():
                self.construct_for(tag)
            case AssignmentTag():
                self.construct_assignment(tag)
            case StyleTag() if self.layout is None:
                self.construct_style(tag)
            case SlotTag():
                self.construct_slot_tag(tag)
            case StyleTag():  #  if self.layout
                # Type narrow doesn't work properly
                pass
            case e:
                assert_never(e)

    def create_block(self, tags: Sequence[TemplateTag]) -> Sequence[ast.stmt]:
        if not self.buffer.empty():
            raise RuntimeError("Internal Error, must flush buffer before creating block")

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
        name: str | ast.Name,
        tags: Sequence[TemplateTag],
    ) -> list[ast.stmt]:
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
            ast.Assign(
                targets=[tag.target],
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
                value=ast_utils.Add(
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

        elif_blocks: list[tuple[ast.expr, Sequence[ast.stmt]]] = []
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

    def construct_for(self, block: ForTag):
        self.enter_block()
        for_body = self.create_block(block.loop_block)
        if len(for_body) > 0:
            self.body.append(
                ast.For(
                    target=block.loop_variable,
                    iter=block.iterable,
                    body=for_body,
                    orelse=[],
                )
            )

    def construct_block_tag(self, block: parse_ast.BlockTag):
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

    def create_subcontext(self, name: str | ast.Name | None = None):
        if name is None:
            variable = self.variable
        else:
            variable = StringVariable(name)

        return CodeBuilder(
            variable=variable, template=self.template, layout=self.layout, css=self.css
        )
