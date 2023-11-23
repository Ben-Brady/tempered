from ..parser import parse_ast
from ..parser.parse_ast import (
    Template,
    LayoutTemplate,
    TemplateTag,
    LiteralBlock,
    ExprBlock,
    HtmlBlock,
    ComponentBlock,
    StyleBlock,
    IfBlock,
    ForBlock,
    AssignmentBlock,
    SlotBlock,
)
from .. import ast_utils
from .utils import (
    create_escape_call,
    slot_variable_name,
    slot_parameter,
    WITH_STYLES_PARAMETER,
    LAYOUT_CSS_PARAMETER,
    COMPONENT_CSS_VARIABLE,
    KWARGS_VARIABLE,
)
from .accumulators import Result, StringResult
import ast
from typing_extensions import Sequence, assert_never, Protocol
from dataclasses import dataclass


@dataclass
class BuildContext:
    result: Result

    template: Template
    layout: LayoutTemplate | None
    css: str


def construct_tag(tag: TemplateTag, ctx: BuildContext) -> Sequence[ast.stmt]:
    match tag:
        case LiteralBlock():
            return [ctx.result.create_add(ast_utils.Constant(tag.body))]
        case ExprBlock():
            return [ctx.result.create_add(create_escape_call(tag.value))]
        case HtmlBlock():
            return [ctx.result.create_add(tag.value)]
        case ComponentBlock():
            return construct_component_tag(ctx, tag)
        case StyleBlock() if ctx.layout is None:
            return construct_style(ctx, tag)
        case StyleBlock():
            # If a component has a layout, the styles will be placed there
            return []
        case IfBlock():
            return construct_if(ctx, tag)
        case ForBlock():
            return construct_for(ctx, tag)
        case AssignmentBlock():
            return construct_assignment(ctx, tag)
        case SlotBlock():
            return construct_slot_tag(ctx, tag)
        case parse_ast.BlockBlock():
            return construct_block_tag(ctx, tag)
        case e:
            assert_never(e)


def construct_block(
    ctx: BuildContext, tags: Sequence[TemplateTag]
) -> Sequence[ast.stmt]:
    block: list[ast.stmt] = []
    for tag in tags:
        block.extend(construct_tag(tag, ctx))

    return block


def construct_component_tag(
    ctx: BuildContext, tag: ComponentBlock
) -> Sequence[ast.stmt]:
    func = ast_utils.Name(tag.component_name)
    keywords = tag.keywords.copy()
    keywords[WITH_STYLES_PARAMETER] = ast_utils.Constant(False)

    func_call = ast_utils.Call(
        func=func,
        keywords=keywords,
        kwargs=ast_utils.Name(KWARGS_VARIABLE),
    )
    return [ctx.result.create_add(func_call)]


def construct_assignment(ctx: BuildContext, tag: AssignmentBlock) -> Sequence[ast.stmt]:
    return [
        ast.Assign(
            targets=[tag.target],
            value=tag.value,
        )
    ]


def construct_style(ctx: BuildContext, tag: StyleBlock) -> Sequence[ast.stmt]:
    if isinstance(ctx.template, LayoutTemplate):
        css_variables = LAYOUT_CSS_PARAMETER, COMPONENT_CSS_VARIABLE
    else:
        css_variables = (COMPONENT_CSS_VARIABLE,)
    return [
        ast_utils.If(
            condition=ast_utils.And(
                ast_utils.Name(WITH_STYLES_PARAMETER),
                ast_utils.Name(COMPONENT_CSS_VARIABLE),
            ),
            if_body=[
                ctx.result.create_add(
                    ast_utils.Add(
                        ast_utils.Constant("<style>"),
                        ast_utils.Name(COMPONENT_CSS_VARIABLE),
                        ast_utils.Constant("</style>"),
                    ),
                )
            ],
        )
    ]


def construct_if(ctx: BuildContext, block: IfBlock) -> Sequence[ast.stmt]:
    if_body = construct_block(ctx, block.if_block)
    if block.else_block:
        else_body = construct_block(ctx, block.else_block)
    else:
        else_body = None

    elif_blocks = [
        (condition, construct_block(ctx, elif_block))
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


def construct_for(ctx: BuildContext, block: ForBlock) -> Sequence[ast.stmt]:
    body: list[ast.stmt] = []
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


def construct_block_tag(
    ctx: BuildContext, block: parse_ast.BlockBlock
) -> Sequence[ast.stmt]:
    return construct_block_assign(
        ctx=ctx,
        target=slot_variable_name(block.name),
        block=block.body,
    )


def construct_slot_tag(ctx: BuildContext, tag: SlotBlock) -> Sequence[ast.stmt]:
    body: list[ast.stmt] = []
    slot_param = ast_utils.Name(slot_parameter(tag.name))

    if tag.default is not None:
        if_body = construct_block_assign(
            ctx=ctx,
            target=slot_param,
            block=tag.default,
        )

        body.append(
            ast_utils.If(
                condition=ast_utils.Is(slot_param, ast_utils.None_),
                if_body=if_body,
            )
        )

    body.append(ctx.result.create_add(slot_param))
    return body


def construct_block_assign(
    ctx: BuildContext,
    target: str | ast.Name,
    block: parse_ast.TemplateBlock,
) -> list[ast.stmt]:
    body: list[ast.stmt] = []
    if block == []:
        return [ast_utils.Assign(target, ast_utils.EmptyStr)]

    if len(block) == 1 and isinstance(block[0], LiteralBlock):
        return [ast_utils.Assign(target, ast_utils.Constant(block[0].body))]
    else:
        with use_temporary_output(ctx, target):
            ctx.result = StringResult(target)
            body.extend(ctx.result.create_init())
            body.extend(construct_block(ctx, block))
            body.append(ast_utils.Assign(target, ctx.result.create_value()))

        return body


from contextlib import contextmanager


@contextmanager
def use_temporary_output(
    ctx: BuildContext,
    name: str | ast.Name,
):
    original_result = ctx.result

    try:
        ctx.result = StringResult(name)
        yield
    finally:
        ctx.result = original_result
