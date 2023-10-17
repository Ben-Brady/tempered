from ..parse.parse_ast import *
from ..ast_utils import (
    create_constant, create_call, create_escape_call, create_add_assign,
    create_name, create_if, create_string_concat
)
from .constants import style_constant
import ast
from typing import Sequence, assert_never
from dataclasses import dataclass, field


@dataclass
class BuildContext:
    template: Template
    result_value: ast.Name


def construct_tag(tag: TemplateTag, ctx: BuildContext) -> Sequence[ast.AST]:
    match tag:
        case LiteralBlock():
            return [create_add_assign(
                target=ctx.result_value,
                value=create_constant(tag.body),
            )]
        case ExprBlock():
            return [create_add_assign(
                target=ctx.result_value,
                value=create_escape_call(tag.value),
            )]
        case HtmlBlock():
            return [create_add_assign(
                target=ctx.result_value,
                value=tag.value,
            )]
        case ComponentBlock():
            return [create_add_assign(
                target=ctx.result_value,
                value=tag.component_call,
            )]
        case IncludeStyleBlock():
            return [create_add_assign(
                target=ctx.result_value,
                value=style_constant(tag.template),
            )]
        case StyleBlock():
            return construct_style(tag, ctx)
        case IfBlock():
            return construct_if(tag, ctx)
        case ForBlock():
            return construct_for(tag, ctx)
        case e:
            assert_never(e)



def construct_style_include(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    if_body = [create_add_assign(
        target=ctx.result_value,
        value=create_string_concat(
            style_constant(ctx.template.name),
            *(
                style_constant(name)
                for name in ctx.template.child_components
            )
        )
    )]

    return [create_if(
        condition=create_name("with_styles"),
        if_body=if_body,
    )]

def construct_style(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    if_body = [create_add_assign(
        target=ctx.result_value,
        value=create_string_concat(
            style_constant(ctx.template.name),
            *(
                style_constant(name)
                for name in ctx.template.child_components
            )
        )
    )]

    return [create_if(
        condition=create_name("with_styles"),
        if_body=if_body,
    )]

def construct_if(block: IfBlock, ctx: BuildContext) -> Sequence[ast.AST]:
    if_block = []
    else_block = []

    for tag in block.if_block:
        if_block.extend(construct_tag(tag, ctx))

    if block.else_block:
        for tag in block.else_block:
            else_block.extend(construct_tag(tag, ctx))

    return [
        ast.If(
            test=block.condition,
            body=if_block,
            orelse=else_block,
        )
    ]


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
