from ...preprocess import generate_scoped_styles, minify_html
from ..parse_ast import *
from ..lexer import *
from .scanner import TokenScanner
from .expr import parse_expr, parse_parameter, parse_ident
import ast

def create_body(scanner: TokenScanner) -> TemplateBlock:
    tags = []
    while scanner.has_tokens:
        tag = next_tag(scanner)
        tags.append(tag)

    return tags


def next_tag(scanner: TokenScanner) -> TemplateTag:
    match scanner.pop():
        case (LiteralToken() | StylesToken() | StylesIncludeToken()) as tag:
            return tag.into_tag()
        case EscapedExprToken(expr_str):
            return ExprBlock(parse_expr(expr_str))
        case HtmlExprToken(expr_str):
            return HtmlBlock(parse_expr(expr_str))
        case ComponentToken(template=template, expr=expr_str):
            return parse_component_block(template, expr_str)
        case IfStartToken(condition):
            return next_if(scanner, condition)
        case ForStartToken(variable, iterable):
            return next_for(scanner, variable, iterable)
        case ForEndToken():
            raise ValueError(f"For loop not opened")
        case ElIfToken() | ElseToken() | IfEndToken():
            raise ValueError(f"If statement not openned")
        case e:
            raise ValueError(f"Unexpected {e}")


def parse_component_block(
        template: str,
        expr: str,
        ) -> ComponentBlock:
    call = parse_expr(expr)
    if not isinstance(call, ast.Call):
        raise ValueError("Component call must be a function call")

    return ComponentBlock(
        component_name=template,
        component_call=call,
    )


def next_if(
        scanner: TokenScanner,
        condition_str: str,
        ) -> IfBlock:
    condition = parse_expr(condition_str)

    if_block: list[TemplateTag] = []
    while not scanner.is_next(ElIfToken, ElseToken, IfEndToken):
        tag = next_tag(scanner)
        if_block.append(tag)

    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = []
    while scanner.is_next(ElIfToken):
        elif_token = scanner.expect(ElIfToken)
        elif_condition = parse_expr(elif_token.condition)

        block: list[TemplateTag] = []
        while not scanner.is_next(ElIfToken, ElseToken, IfEndToken):
            tag = next_tag(scanner)
            block.append(tag)

        elif_blocks.append((elif_condition, block))

    else_block: list[TemplateTag] | None = None
    if scanner.accept(ElseToken):
        else_block = []
        while not scanner.is_next(IfEndToken):
            tag = next_tag(scanner)
            else_block.append(tag)


    scanner.expect(IfEndToken)
    return IfBlock(
        condition=condition,
        if_block=if_block,
        else_block=else_block,
        elif_blocks=elif_blocks,
    )


def next_for(
        scanner: TokenScanner,
        variable_str: str,
        iterable_str: str,
        ) -> ForBlock:
    loop_var = parse_ident(variable_str)
    iterable = parse_expr(iterable_str)

    block = []
    while not scanner.is_next(ForEndToken):
        tag = next_tag(scanner)
        block.append(tag)

    scanner.expect(ForEndToken)
    return ForBlock(
        loop_block=block,
        iterable=iterable,
        loop_variable=loop_var,
    )
