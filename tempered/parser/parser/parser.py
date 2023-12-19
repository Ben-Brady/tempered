from .. import template_ast, tokens
from ..lexer import *
from .token_scanner import TokenScanner
from .expr import parse_expr, parse_stmt, parse_ident, parse_parameter
import typing_extensions as t
import ast
from dataclasses import dataclass, field


@dataclass
class ParseContext:
    is_layout: bool = False
    parameters: t.List[template_ast.TemplateParameter] = field(default_factory=list)
    layout: t.Union[str, None] = None

    has_default_slot: bool = False
    slots: t.List[template_ast.SlotTag] = field(default_factory=list)

    components_calls: t.List[template_ast.ComponentTag] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)
    body: template_ast.TemplateBlock = field(default_factory=list)
    styles_set: bool = False
    blocks: t.Set[str] = field(default_factory=set)


def parse_token_stream(tokens: t.Sequence[tokens.Token], has_css: bool) -> ParseContext:
    scanner = TokenScanner(tokens)
    ctx = ParseContext()
    ctx.body = take_tags_until(ctx, scanner)

    if not ctx.styles_set:
        has_children = len(ctx.style_includes) > 0 or len(ctx.components_calls) > 0
        if ctx.is_layout or has_css or has_children:
            ctx.body = [*ctx.body, template_ast.StyleTag()]

    return ctx


def take_tags_until(
    ctx: ParseContext,
    scanner: TokenScanner,
    stop_tags: t.List[t.Type[tokens.Token]] = [],
) -> t.List[template_ast.TemplateTag]:
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(ctx, scanner)
        if tag:
            tags.append(tag)

    return tags


def next_tag(ctx: ParseContext, scanner: TokenScanner) -> t.Union[template_ast.TemplateTag, None]:
    tag = scanner.pop()
    if isinstance(tag, tokens.LiteralToken):
        return tag.into_tag()
    elif isinstance(tag, tokens.StylesIncludeToken):
        ctx.style_includes.add(tag.template)
        return None
    elif isinstance(tag, tokens.EscapedExprToken):
        return template_ast.ExprTag(parse_expr(tag.expr))
    elif isinstance(tag, tokens.HtmlExprToken):
        return template_ast.HtmlTag(parse_expr(tag.expr))
    elif isinstance(tag, tokens.ComponentToken):
        return next_component(ctx, tag)
    elif isinstance(tag, tokens.StylesToken):
        return parse_styles(ctx)
    elif isinstance(tag, tokens.LayoutToken):
        parse_layout(ctx, tag.layout)
        return None
    elif isinstance(tag, tokens.ParameterToken):
        parse_param(ctx, tag)
        return None
    elif isinstance(tag, tokens.SetToken):
        return next_set(tag)

    elif isinstance(tag, tokens.SlotToken):
        return next_slot(ctx, scanner, tag)
    elif isinstance(tag, tokens.SlotEndToken):
        raise ValueError("Slot not opened")

    elif isinstance(tag, tokens.BlockToken):
        return next_block(ctx, scanner, tag)
    elif isinstance(tag, tokens.BlockEndToken):
        raise ValueError("Block not opened")

    elif isinstance(tag, tokens.IfStartToken):
        return next_if(ctx, scanner, tag)
    elif isinstance(tag, (tokens.ElIfToken, tokens.ElseToken, tokens.IfEndToken)):
        raise ValueError("If statement not openned")

    elif isinstance(tag, tokens.ForStartToken):
        return next_for(ctx, scanner, tag)
    elif isinstance(tag, tokens.ForEndToken):
        raise ValueError("For loop not opened")
    else:
        t.assert_never(tag)


def next_slot(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.SlotToken
    ) -> template_ast.SlotTag:
    ctx.is_layout = True

    if token.name is None:
        if ctx.has_default_slot:
            raise ValueError("Template cannot have multiple default slots")

        ctx.has_default_slot = True
        return template_ast.SlotTag(name=None, default=None)


    if token.is_required:
        default_body = None
    else:
        default_body = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.SlotEndToken]
        )
        scanner.expect(tokens.SlotEndToken)

    slot = template_ast.SlotTag(
        name=token.name,
        default=default_body,
    )
    ctx.slots.append(slot)
    return slot


def parse_styles(ctx: ParseContext) -> template_ast.StyleTag:
    if ctx.styles_set:
        raise ValueError("Template cannot have multiple styles tags")

    ctx.styles_set = True
    return template_ast.StyleTag()


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


def next_component(ctx: ParseContext, token: tokens.ComponentToken) -> template_ast.ComponentTag:
    call = parse_expr(token.call)
    if (
        not isinstance(call, ast.Call) or
        not isinstance(call.func, ast.Name)):
        raise ValueError("Invalid Component Call")

    call = template_ast.ComponentTag(
        component_name=call.func.id,
        keywords={
            keyword.arg: keyword.value
            for keyword in call.keywords
            if keyword.arg is not None
        },
    )
    ctx.components_calls.append(call)
    return call


def next_set(token: tokens.SetToken) -> template_ast.AssignmentTag:
    call = parse_stmt(token.assignment)
    if isinstance(call, ast.Assign):
        if len(call.targets) != 1:
            raise ValueError("Set must have a single target")

        return template_ast.AssignmentTag(
            target=call.targets[0],
            value=call.value,
        )
    elif isinstance(call, ast.AnnAssign):
        if call.value is None:
            raise ValueError("Set must have a value")

        return template_ast.AssignmentTag(
            target=call.target,
            value=call.value,
        )
    else:
        raise ValueError("Set must be an assignment")


def next_if(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.IfStartToken,
) -> template_ast.IfTag:
    condition = parse_expr(token.condition)

    if_block: t.List[template_ast.TemplateTag] = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[
            tokens.ElIfToken,
            tokens.ElseToken,
            tokens.IfEndToken,
        ]
    )

    elif_blocks: t.List[t.Tuple[ast.expr, template_ast.TemplateBlock]] = []
    while scanner.is_next(tokens.ElIfToken):
        elif_token = scanner.expect(tokens.ElIfToken)
        elif_condition = parse_expr(elif_token.condition)
        block: t.List[template_ast.TemplateTag] = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[
                tokens.ElIfToken,
                tokens.ElseToken,
                tokens.IfEndToken
            ],
        )
        elif_blocks.append((elif_condition, block))

    else_block: t.Union[t.List[template_ast.TemplateTag], None] = None
    if scanner.accept(tokens.ElseToken):
        else_block = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.IfEndToken],
        )

    scanner.expect(tokens.IfEndToken)
    return template_ast.IfTag(
        condition=condition,
        if_block=if_block,
        else_block=else_block,
        elif_blocks=elif_blocks,
    )


def next_for(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.ForStartToken,
) -> template_ast.ForTag:
    loop_var = parse_ident(token.variable)
    iterable = parse_expr(token.iterable)

    block = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[tokens.ForEndToken],
    )
    scanner.expect(tokens.ForEndToken)

    return template_ast.ForTag(
        loop_block=block,
        iterable=iterable,
        loop_variable=loop_var,
    )


def next_block(
    ctx: ParseContext,
    scanner: TokenScanner,
    token: tokens.BlockToken,
) -> template_ast.BlockTag:
    ctx.blocks.add(token.name)
    body = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[tokens.BlockEndToken],
    )
    scanner.expect(tokens.BlockEndToken)

    return template_ast.BlockTag(
        name=token.name,
        body=body,
    )
