from ..parser.parse_ast import (
    Template, TemplateTag, LiteralBlock, ExprBlock, HtmlBlock, IncludeStyleBlock,
    ComponentBlock, StyleBlock, IfBlock, ForBlock, AssignmentBlock
)
from ..ast_utils import (
    create_constant, create_call, create_assignment,
    create_name, create_if, create_string_concat, create_attribute
)
from .utils import create_style_name, create_escape_call, WITH_STYLES_PARAMETER
from .accumulators import Result
import ast
from typing import Sequence, assert_never, Protocol
from dataclasses import dataclass


@dataclass
class BuildContext:
    template: Template
    result: Result


def construct_tag(tag: TemplateTag, ctx: BuildContext) -> Sequence[ast.AST]:
    match tag:
        case LiteralBlock():
            return [ctx.result.create_add(create_constant(tag.body))]
        case ExprBlock():
            return [ctx.result.create_add(create_escape_call(tag.value))]
        case HtmlBlock():
            return [ctx.result.create_add(tag.value)]
        case IncludeStyleBlock():
            return [ctx.result.create_add(create_style_name(tag.template))]
        case ComponentBlock():
            return construct_component_tag(tag, ctx)
        case StyleBlock():
            return construct_style(tag, ctx)
        case IfBlock():
            return construct_if(tag, ctx)
        case ForBlock():
            return construct_for(tag, ctx)
        case AssignmentBlock():
            return construct_assignment(tag, ctx)
        case e:
            assert_never(e)


def construct_block(tags: Sequence[TemplateTag], ctx: BuildContext) -> list[ast.stmt]:
    block = []
    for tag in tags:
        block.extend(construct_tag(tag, ctx))

    return block


def construct_component_tag(tag: ComponentBlock, ctx: BuildContext) -> list[ast.AST]:
    func = create_name(tag.component_name)
    keywords = tag.keywords.copy()
    keywords[WITH_STYLES_PARAMETER] = create_constant(False)

    func_call = create_call(func, keywords=keywords)
    return [ctx.result.create_add(func_call)]


def construct_assignment(tag: AssignmentBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    return [ast.Assign(
        targets=[tag.target],
        value=tag.value,
    )]


def construct_style_include(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    value = create_string_concat(
        create_style_name(ctx.template.name),
        *(
            create_style_name(name)
            for name in ctx.template.child_components
        )
    )

    return [create_if(
        condition=create_name("with_styles"),
        if_body=[ctx.result.create_add(value)],
    )]


def construct_style(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    value = create_string_concat(
        create_constant("<style>"),
        create_style_name(ctx.template.name),
        *(
            create_style_name(name)
            for name in ctx.template.child_components
        ),
        create_constant("</style>"),
    )

    return [create_if(
        condition=create_name("with_styles"),
        if_body=[ctx.result.create_add(value)],
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
