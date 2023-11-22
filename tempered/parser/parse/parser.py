from ..css import tranform_css, minify_html
from .. import parse_ast, tokens
from ..lexer import *
from .token_scanner import TokenScanner
from .expr import parse_expr, parse_stmt, parse_ident, parse_parameter
from typing_extensions import assert_never, Literal
import ast
from dataclasses import dataclass, field


@dataclass
class ParseContext:
    is_layout: bool = False
    parameters: list[parse_ast.TemplateParameter] = field(default_factory=list)
    layout: str|None = None

    has_default_slot: bool = False
    slots: list[parse_ast.SlotBlock] = field(default_factory=list)

    components_calls: list[parse_ast.ComponentBlock] = field(default_factory=list)
    style_includes: set[str] = field(default_factory=set)
    body: parse_ast.TemplateBlock = field(default_factory=list)
    styles_set: bool = False
    blocks: set[str] = field(default_factory=set)


def parse_token_stream(tokens: Sequence[tokens.Token]) -> ParseContext:
    scanner = TokenScanner(tokens)
    ctx = ParseContext()
    ctx.body = take_tags_until(ctx, scanner)

    if not ctx.styles_set:
        ctx.body = [*ctx.body, parse_ast.StyleBlock()]

    return ctx


def take_tags_until(
    ctx: ParseContext,
    scanner: TokenScanner,
    stop_tags: list[type[tokens.Token]] = [],
) -> list[parse_ast.TemplateTag]:
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(ctx, scanner)
        if tag:
            tags.append(tag)

    return tags


def next_tag(ctx: ParseContext, scanner: TokenScanner) -> parse_ast.TemplateTag | None:
    token = scanner.pop()
    match token:
        case tokens.LiteralToken() as tag:
            return tag.into_tag()
        case tokens.StylesIncludeToken() as tag:
            ctx.style_includes.add(tag.template)
            return None
        case tokens.EscapedExprToken(expr_str):
            return parse_ast.ExprBlock(parse_expr(expr_str))
        case tokens.HtmlExprToken(expr_str):
            return parse_ast.HtmlBlock(parse_expr(expr_str))
        case tokens.ComponentToken() as token:
            return next_component(ctx, token)
        case tokens.StylesToken():
            return parse_styles(ctx)
        case tokens.LayoutToken(layout):
            parse_layout(ctx, layout)
            return None
        case tokens.ParameterToken() as token:
            parse_param(ctx, token)
            return None
        case tokens.SetToken() as token:
            return next_set(token)

        case tokens.SlotToken() as token:
            return next_slot(ctx, scanner, token)
        case tokens.SlotEndToken():
            raise ValueError("Slot not opened")

        case tokens.BlockToken(name) as token:
            return next_block(ctx, scanner, token)
        case tokens.BlockEndToken():
            raise ValueError("Block not opened")

        case tokens.IfStartToken() as token:
            return next_if(ctx, scanner, token)
        case tokens.ElIfToken() | tokens.ElseToken() | tokens.IfEndToken():
            raise ValueError("If statement not openned")

        case tokens.ForStartToken() as token:
            return next_for(ctx, scanner, token)
        case tokens.ForEndToken():
            raise ValueError("For loop not opened")
        case e:
            assert_never(e)


def next_slot(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.SlotToken
    ) -> parse_ast.SlotBlock:
    ctx.is_layout = True

    if token.name is None:
        if ctx.has_default_slot:
            raise ValueError("Template cannot have multiple default slots")

        ctx.has_default_slot = True
        return parse_ast.SlotBlock(name=None, default=None)


    if token.is_required:
        default_body = None
    else:
        default_body = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.SlotEndToken]
        )
        scanner.expect(tokens.SlotEndToken)

    slot = parse_ast.SlotBlock(
        name=token.name,
        default=default_body,
    )
    ctx.slots.append(slot)
    return slot


def parse_styles(ctx: ParseContext) -> parse_ast.StyleBlock:
    if ctx.styles_set:
        raise ValueError("Template cannot have multiple styles tags")

    ctx.styles_set = True
    return parse_ast.StyleBlock()


def parse_layout(ctx: ParseContext, layout_str: str) -> None:
    if ctx.layout is not None:
        raise ValueError("Template cannot have multiple layout tags")

    layout = ast.literal_eval(layout_str)
    if not isinstance(layout, str):
        raise ValueError("Template names must be a string")

    ctx.layout = layout
    return None


def parse_param(ctx: ParseContext, token: tokens.ParameterToken) -> None:
    param = parse_parameter(token.parameter)
    ctx.parameters.append(param)
    return None


def next_component(ctx: ParseContext, token: tokens.ComponentToken) -> parse_ast.ComponentBlock:
    call = parse_expr(token.call)
    match call:
        case ast.Call(
            func=ast.Name(id=component_name),
            keywords=keywords,
        ):
            call = parse_ast.ComponentBlock(
                component_name=component_name,
                keywords={
                    keyword.arg: keyword.value
                    for keyword in keywords
                    if keyword.arg is not None
                },
            )
            ctx.components_calls.append(call)
            return call
        case _:
            raise ValueError("Invalid Component Call")


def next_set(token: tokens.SetToken) -> parse_ast.AssignmentBlock:
    call = parse_stmt(token.assignment)
    if isinstance(call, ast.Assign):
        if len(call.targets) != 1:
            raise ValueError("Set must have a single target")

        return parse_ast.AssignmentBlock(
            target=call.targets[0],
            value=call.value,
        )
    elif isinstance(call, ast.AnnAssign):
        if call.value is None:
            raise ValueError("Set must have a value")

        return parse_ast.AssignmentBlock(
            target=call.target,
            value=call.value,
        )
    else:
        raise ValueError("Set must be an assignment")


def next_if(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.IfStartToken,
) -> parse_ast.IfBlock:
    condition = parse_expr(token.condition)

    if_block: list[parse_ast.TemplateTag] = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[
            tokens.ElIfToken,
            tokens.ElseToken,
            tokens.IfEndToken,
        ]
    )

    elif_blocks: list[tuple[ast.expr, parse_ast.TemplateBlock]] = []
    while scanner.is_next(tokens.ElIfToken):
        elif_token = scanner.expect(tokens.ElIfToken)
        elif_condition = parse_expr(elif_token.condition)
        block: list[parse_ast.TemplateTag] = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[
                tokens.ElIfToken,
                tokens.ElseToken,
                tokens.IfEndToken
            ],
        )
        elif_blocks.append((elif_condition, block))

    else_block: list[parse_ast.TemplateTag] | None = None
    if scanner.accept(tokens.ElseToken):
        else_block = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.IfEndToken],
        )

    scanner.expect(tokens.IfEndToken)
    return parse_ast.IfBlock(
        condition=condition,
        if_block=if_block,
        else_block=else_block,
        elif_blocks=elif_blocks,
    )


def next_for(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.ForStartToken,
) -> parse_ast.ForBlock:
    loop_var = parse_ident(token.variable)
    iterable = parse_expr(token.iterable)

    block = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[tokens.ForEndToken],
    )
    scanner.expect(tokens.ForEndToken)

    return parse_ast.ForBlock(
        loop_block=block,
        iterable=iterable,
        loop_variable=loop_var,
    )


def next_block(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.BlockToken,
) -> parse_ast.BlockBlock:
    ctx.blocks.add(token.name)
    body = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[tokens.BlockEndToken],
    )
    scanner.expect(tokens.BlockEndToken)

    return parse_ast.BlockBlock(
        name=token.name,
        body=body,
    )
