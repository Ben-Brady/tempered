from ...preprocess import preprocess_style_tags, minify_html
from ..parse_ast import *
from ..lexer import *
from .scanner import TokenScanner
from .expr import parse_expr, parse_parameter, parse_ident
from typing import LiteralString, Any, Sequence


def parse_template(
        name: str,
        template_html: LiteralString,
        context: dict[str, Any]|None = None
        ) -> Template:
    context = context or {}

    html = template_html
    html = minify_html(html)
    html, css = preprocess_style_tags(html)
    tokens = to_token_stream(html)

    tokens, params = extract_parameters(tokens)

    scanner = TokenScanner(tokens)
    child_components = get_child_components(tokens)
    body = create_body(scanner)

    return Template(
        name=name,
        parameters=params,
        context=context,
        body=body,
        child_components=child_components,
        style=css,
    )


def extract_parameters(tokens: Sequence[Token]) -> tuple[Sequence[Token], list[TemplateParameter]]:
    parameters = [
        parse_parameter(token.parameter)
        for token in tokens
        if isinstance(token, ParameterToken)
    ]
    tokens = [
        token for token in tokens
        if not isinstance(token, ParameterToken)
    ]
    return tokens, parameters



def get_child_components(tokens: Sequence[Token]) -> list[str]:
    return [
        token.template
        for token in tokens
        if isinstance(token, ComponentToken)
    ]


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
            return ComponentBlock(
                component_name=template,
                component_call=parse_expr(expr_str),
            )
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



def next_if(
        scanner: TokenScanner,
        condition_str: str,
        ) -> IfBlock:
    condition = parse_expr(condition_str)

    if_block = []
    while not scanner.is_next(ElIfToken, ElseToken, IfEndToken):
        tag = next_tag(scanner)
        if_block.append(tag)

    elif_blocks = []
    while scanner.is_next(ElIfToken):
        elif_token = scanner.expect(ElIfToken)
        elif_condition = parse_expr(elif_token.condition)

        block = []
        while not scanner.is_next(ElIfToken, ElseToken, IfEndToken):
            tag = next_tag(scanner)
            block.append(tag)

        elif_blocks.append((elif_condition, block))

    else_block = []
    if scanner.accept(ElseToken):
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

