from ...preprocess import generate_scoped_styles, minify_html
from ..parse_ast import *
from ..tokens import *
from ..lexer import *
from .token_scanner import TokenScanner
from .expr import parse_expr, parse_stmt, parse_ident, parse_parameter
from typing_extensions import assert_never
import ast
from dataclasses import dataclass, field


@dataclass
class ParseContext:
    template_type: TemplateType = "component"
    parameters: list[TemplateParameter] = field(default_factory=list)
    layout: str|None = None
    slots: list[TemplateSlot] = field(default_factory=list)
    child_components: set[str] = field(default_factory=set)
    body: TemplateBlock = field(default_factory=list)
    styles_set: bool = False


def parse_tokens(scanner: TokenScanner) -> ParseContext:
    ctx = ParseContext()
    ctx.body = take_tags_until(ctx, scanner, stop_tags=[])
    if ctx.template_type == "layout" and len(ctx.slots) == 0:
        raise ValueError("A layout must have at lease one slot")

    if not ctx.styles_set:
        ctx.body = [*ctx.body, StyleBlock()]

    return ctx


def take_tags_until(
    ctx: ParseContext,
    scanner: TokenScanner,
    stop_tags: list[type[Token]],
) -> list[TemplateTag]:
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(ctx, scanner)
        if tag:
            tags.append(tag)

    return tags


def next_tag(ctx: ParseContext, scanner: TokenScanner) -> TemplateTag | None:
    match scanner.pop():
        case (LiteralToken() | StylesIncludeToken()) as tag:
            return tag.into_tag()
        case StylesToken():
            return parse_styles(ctx)
        case ExtendsToken(layout):
            parse_extends(ctx, layout)
        case ParameterToken(parameter):
            parse_param(ctx, parameter)
        case EscapedExprToken(expr_str):
            return ExprBlock(parse_expr(expr_str))
        case HtmlExprToken(expr_str):
            return HtmlBlock(parse_expr(expr_str))
        case SlotToken(name):
            return parse_slot(ctx, name)
        case ComponentToken(call=call):
            return parse_component_block(ctx, call)
        case SetToken(assignment):
            return parse_set_block(assignment)
        case IfStartToken(condition):
            return next_if(ctx, scanner, condition)
        case ElIfToken() | ElseToken() | IfEndToken():
            raise ValueError(f"If statement not openned")
        case ForStartToken(variable, iterable):
            return next_for(ctx, scanner, variable, iterable)
        case ForEndToken():
            raise ValueError(f"For loop not opened")
        case e:
            assert_never(e)


def parse_slot(ctx: ParseContext, name: str | None) -> SlotBlock:
    ctx.slots.append(TemplateSlot(
        name=name,
        default=None,
    ))
    ctx.template_type = "layout"
    return SlotBlock(name)


def parse_styles(ctx: ParseContext) -> StyleBlock:
    if ctx.styles_set:
        raise ValueError("Template cannot have multiple styles tags")

    ctx.styles_set = True
    return StyleBlock()


def parse_extends(ctx: ParseContext, layout_str: str) -> None:
    if ctx.layout is not None:
        raise ValueError("Template cannot have multiple layout tags")

    layout = ast.literal_eval(layout_str)
    if not isinstance(layout, str):
        raise ValueError("Template names must be a string")

    ctx.layout = layout
    return None


def parse_param(ctx: ParseContext, parameter: str) -> None:
    ctx.parameters.append(parse_parameter(parameter))
    return None


def parse_component_block(ctx: ParseContext, call_str: str) -> ComponentBlock:
    call = parse_expr(call_str)
    match call:
        case ast.Call(
            func=ast.Name(id=component_name),
            keywords=keywords,
        ):
            ctx.child_components.add(component_name)
            return ComponentBlock(
                component_name=component_name,
                keywords={
                    keyword.arg: keyword.value
                    for keyword in keywords
                    if keyword.arg is not None
                },
            )
        case _:
            raise ValueError("Invalid Component Call")


def parse_set_block(assignment: str) -> AssignmentBlock:
    call = parse_stmt(assignment)
    if isinstance(call, ast.Assign):
        if len(call.targets) != 1:
            raise ValueError("Set must have a single target")

        return AssignmentBlock(
            target=call.targets[0],
            value=call.value,
        )
    elif isinstance(call, ast.AnnAssign):
        if call.value is None:
            raise ValueError("Set must have a value")

        return AssignmentBlock(
            target=call.target,
            value=call.value,
        )
    else:
        raise ValueError("Set must be an assignment")


def next_if(
    ctx: ParseContext,
    scanner: TokenScanner,
    condition_str: str,
) -> IfBlock:
    condition = parse_expr(condition_str)

    if_block: list[TemplateTag] = take_tags_until(
        ctx=ctx, scanner=scanner, stop_tags=[ElIfToken, ElseToken, IfEndToken]
    )

    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = []
    while scanner.is_next(ElIfToken):
        elif_token = scanner.expect(ElIfToken)
        elif_condition = parse_expr(elif_token.condition)
        block: list[TemplateTag] = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[ElIfToken, ElseToken, IfEndToken],
        )
        elif_blocks.append((elif_condition, block))

    else_block: list[TemplateTag] | None = None
    if scanner.accept(ElseToken):
        else_block = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[IfEndToken],
        )

    scanner.expect(IfEndToken)
    return IfBlock(
        condition=condition,
        if_block=if_block,
        else_block=else_block,
        elif_blocks=elif_blocks,
    )


def next_for(
    ctx: ParseContext,
    scanner: TokenScanner,
    variable_str: str,
    iterable_str: str,
) -> ForBlock:
    loop_var = parse_ident(variable_str)
    iterable = parse_expr(iterable_str)

    block = take_tags_until(
        ctx=ctx,
        scanner=scanner,
        stop_tags=[ForEndToken],
    )
    scanner.expect(ForEndToken)

    return ForBlock(
        loop_block=block,
        iterable=iterable,
        loop_variable=loop_var,
    )
