from ..parser.parse_ast import (
    Template, TemplateTag, LiteralBlock, ExprBlock, HtmlBlock, IncludeStyleBlock,
    ComponentBlock, StyleBlock, IfBlock, ForBlock,
    AssignmentBlock, SlotBlock
)
from .. import ast_utils
from .utils import (
    create_style_name, create_escape_call, WITH_STYLES_PARAMETER,
    create_layout_func_name, create_slot_param, COMPONENT_STYLES
)
from .accumulators import Result
import ast
from typing_extensions import Sequence, assert_never, Protocol
from dataclasses import dataclass


@dataclass
class BuildContext:
    template: Template
    result: Result


def construct_tag(tag: TemplateTag, ctx: BuildContext) -> Sequence[ast.stmt]:
    match tag:
        case LiteralBlock():
            return [ctx.result.create_add(ast_utils.Constant(tag.body))]
        case ExprBlock():
            return [ctx.result.create_add(create_escape_call(tag.value))]
        case HtmlBlock():
            return [ctx.result.create_add(tag.value)]
        case IncludeStyleBlock():
            return [ctx.result.create_add(create_style_name(tag.template))]
        case ComponentBlock():
            return construct_component_tag(tag, ctx)
        case StyleBlock() if ctx.template.layout is None:
            return construct_style(tag, ctx)
        case StyleBlock():
            # If a component has a layout, the styles will be placed there
            return []
        case IfBlock():
            return construct_if(tag, ctx)
        case ForBlock():
            return construct_for(tag, ctx)
        case AssignmentBlock():
            return construct_assignment(tag, ctx)
        case SlotBlock():
            return construct_slot_tag(tag, ctx)
        case e:
            assert_never(e)


def construct_block(tags: Sequence[TemplateTag], ctx: BuildContext) -> Sequence[ast.stmt]:
    block: list[ast.stmt] = []
    for tag in tags:
        block.extend(construct_tag(tag, ctx))

    return block


def construct_slot_tag(tag: SlotBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    param = ast_utils.Name(create_slot_param(tag.name))
    return [ctx.result.create_add(param)]


def construct_component_tag(tag: ComponentBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    func = ast_utils.Name(tag.component_name)
    keywords = tag.keywords.copy()
    keywords[WITH_STYLES_PARAMETER] = ast_utils.Constant(False)

    func_call = ast_utils.Call(func, keywords=keywords)
    return [ctx.result.create_add(func_call)]


def construct_assignment(tag: AssignmentBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    return [ast.Assign(
        targets=[tag.target],
        value=tag.value,
    )]


def construct_style_include(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    value = ast_utils.StringConcat(
        create_style_name(ctx.template.name),
        *(
            create_style_name(name)
            for name in ctx.template.child_components
        )
    )

    return [ast_utils.If(
        condition=ast_utils.Name("with_styles"),
        if_body=[ctx.result.create_add(value)],
    )]


def construct_style(tag: StyleBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    return [ast_utils.If(
        condition=ast_utils.Name("with_styles"),
        if_body=[
            ctx.result.create_add(
                ast_utils.StringConcat(
                    ast_utils.Constant("<style>"),
                    ast_utils.Name(COMPONENT_STYLES),
                    ast_utils.Constant("</style>"),
                )
            )
        ],
    )]


def construct_if(block: IfBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
    if_body = construct_block(block.if_block, ctx)
    if block.else_block:
        else_body = construct_block(block.else_block, ctx)
    else:
        else_body = None

    elif_blocks = [
        (condition, construct_block(elif_block, ctx))
        for condition, elif_block in block.elif_blocks
    ]
    return [
        ast_utils.If(
            condition=block.condition,
            if_body=if_body,
            elif_blocks=elif_blocks,
            else_body=else_body,
        )
    ]


def construct_for(block: ForBlock, ctx: BuildContext) -> Sequence[ast.stmt]:
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
