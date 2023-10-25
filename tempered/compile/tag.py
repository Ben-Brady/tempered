from ..parser.parse_ast import *
from .. import ast_utils
from ..ast_utils import (
    create_constant, create_call, create_escape_call,
    create_name, create_if, create_string_concat, create_attribute
)
from .constants import style_constant
import ast
from typing import Sequence, assert_never, Protocol
from dataclasses import dataclass


class Result(Protocol):
    def create_assignment(self) -> list[ast.AST]:
        ...

    def add(self, value: ast.expr) -> ast.AST:
        ...

    def create_return(self) -> ast.AST:
        ...


class StringResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.create_name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.create_assignment(
            target=self._variable,
            value="",
        )]

    def add(self, value: ast.expr) -> ast.AST:
        return ast_utils.create_add_assign(
            target=self._variable,
            value=value,
        )

    def create_return(self) -> ast.AST:
        return ast.Return(value=self._variable)


class ArrayResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.create_name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.create_assignment(
            target=self._variable,
            value=[],
        )]

    def add(self, value: ast.expr) -> ast.AST:
        return ast.Expr(value=create_call(
            func=create_attribute(self._variable, 'append'),
            args=[value],
        ))

    def create_return(self) -> ast.AST:
        return ast.Return(
            value=ast_utils.construct_array_join(self._variable)
        )


@dataclass
class BuildContext:
    template: Template
    result: Result


def construct_tag(tag: TemplateTag, ctx: BuildContext) -> Sequence[ast.AST]:
    match tag:
        case LiteralBlock():
            return [ctx.result.add(create_constant(tag.body))]
        case ExprBlock():
            return [ctx.result.add(create_escape_call(tag.value))]
        case HtmlBlock():
            return [ctx.result.add(tag.value)]
        case ComponentBlock():
            return [ctx.result.add(tag.component_call)]
        case IncludeStyleBlock():
            return [ctx.result.add(style_constant(tag.template))]
        case StyleBlock():
            return construct_style(tag, ctx)
        case IfBlock():
            return construct_if(tag, ctx)
        case ForBlock():
            return construct_for(tag, ctx)
        case e:
            assert_never(e)


def construct_block(tags: Sequence[TemplateTag], ctx: BuildContext) -> list[ast.stmt]:
    block = []
    for tag in tags:
        block.extend(construct_tag(tag, ctx))

    return block


def construct_style_include(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    value = create_string_concat(
        style_constant(ctx.template.name),
        *(
            style_constant(name)
            for name in ctx.template.child_components
        )
    )

    return [create_if(
        condition=create_name("with_styles"),
        if_body=[ctx.result.add(value)],
    )]


def construct_style(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    value = create_string_concat(
        create_constant("<style>"),
        style_constant(ctx.template.name),
        *(
            style_constant(name)
            for name in ctx.template.child_components
        ),
        create_constant("</style>"),
    )

    return [create_if(
        condition=create_name("with_styles"),
        if_body=[ctx.result.add(value)],
    )]


def construct_if(block: IfBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    def insert_elif(
        if_statement: ast.If,
        condition: ast.expr,
        block: list[ast.stmt]
        ):
        cur_if = if_statement
        while len(cur_if.orelse) == 1 and isinstance(cur_if.orelse[0], ast.If):
            cur_if = cur_if.orelse[0]

        cur_if.orelse = [
            ast.If(
                test=condition,
                body=block,
                orelse=[],
            )
        ]

    def insert_else(
        if_statement: ast.If,
        block: list[ast.stmt]
        ):
        cur_if = if_statement
        while len(cur_if.orelse) == 1 and isinstance(cur_if.orelse[0], ast.If):
            cur_if = cur_if.orelse[0]

        cur_if.orelse = block

    body = construct_block(block.if_block, ctx)
    if_statement = ast.If(
        test=block.condition,
        body=body,
        orelse=[],
    )
    for elif_cond, elif_block in block.elif_blocks:
        insert_elif(if_statement, elif_cond, construct_block(elif_block, ctx))

    if block.else_block is not None:
        insert_else(if_statement, construct_block(block.else_block, ctx))

    return [ if_statement ]


def construct_for(block: ForBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    body = []
    for tag in block.loop_block:
        body.extend(construct_tag(tag, ctx))

    return [
        ast.For(
            target=block.loop_variable,
            iter=block.iterable,
            body=body,
            orelse=[],
        )
    ]
