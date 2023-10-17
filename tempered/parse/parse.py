import ast
from ..preprocess import preprocess_style_tags, minify_html
from .parse_ast import (
    Tag, TemplateBlock, TemplateTag, Template, IfBlock, ForBlock,
    LiteralBlock, ExprBlock, HtmlBlock, ComponentBlock,
    TemplateParameter, RequiredParameter, StyleBlock, IncludeStyleBlock
)
from .tokenise import (
    to_token_stream, TokenType, LiteralToken, EasyParseToken,
    ComponentToken, HtmlExprToken, EscapedExprToken,
    ParameterToken, StylesToken, StylesIncludeToken,
    ForStart, ForEnd,
    IfStartToken, IfEndToken, ElseToken,
)
from typing import LiteralString, Any


def parse_template(
        name: str,
        template_html: LiteralString,
        context: dict[str, Any]|None = None
        ) -> Template:
    context = context or {}

    html = minify_html(template_html)
    html, css = preprocess_style_tags(html)
    html, params = parse_parameters(html)
    tokens = to_token_stream(html)

    return Template(
        name=name,
        parameters=params,
        context=context,
        body=parse_block(tokens),
        child_components=get_child_components(tokens),
        style=css,
    )


def get_parameters(tokens: list[TokenType]) -> list[TemplateParameter]:
    parameters = []
    for token in list(tokens):
        if isinstance(token, ParameterToken):
            tokens.pop(0)
            parameters.append(parse_parameter(token))
        else:
            break


    return parameters



def get_child_components(tokens: list[TokenType]) -> list[str]:
    return [
        token.template
        for token in tokens
        if isinstance(token, ComponentToken)
    ]


def parse_block(tokens: list[TokenType]) -> TemplateBlock:
    tags = []
    while len(tokens) != 0:
        tokens, tag = next_tag(tokens)
        tags.append(tag)

    return []


def next_tag(tokens: list[TokenType]) -> tuple[list[TokenType], TemplateTag]:
    match tokens[0]:
        case (LiteralToken() | StylesToken() | StylesIncludeToken() ) as tag:
            return tokens[1:], tag.into_tag()
        case EscapedExprToken():
            ...
        case HtmlExprToken():
            ...
        case ComponentToken():
            ...
        case ParameterToken():
            raise ValueError(f"Parameters need to be at the top of the template")
        case IfStartToken(condition):
            return next_if(tokens[1:], condition)
        case ForStart(variable, iterable):
            return next_for(tokens[1:], variable, iterable)
        case e:
            raise ValueError(f"Unexpected {e}")


def parse_parameter(parameter: str) -> TemplateParameter:
    module = ast.parse(parameter)
    if not isinstance(module, ast.Module):
        raise ValueError(f"Invalid Parameter: {parameter}")

    expr = module.body[0]
    match expr:
        case ast.Expr(
            value=ast.Name(id=name)
        ):
            return TemplateParameter(name=name)
        case ast.Assign(
            targets=[ast.Name(id=name)],
            value=ast.Constant(value=default)
        ):
            return TemplateParameter(
                name=name,
                default=default
            )
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=ast.Name(id=type)|ast.Constant(value=type),
            value=ast.Name(id=default)|ast.Constant(value=default)
        ):
            return TemplateParameter(
                name=name,
                type=type if isinstance(type, str) else type.id,
                default=default if default is not None else RequiredParameter()
            )
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=ast.Name(id=type)|ast.Constant(value=type),
        ):
            return TemplateParameter(
                name=name,
                type=type if isinstance(type, str) else type.id,
            )
        case _:
            raise ValueError(f"Invalid Parameter: {parameter}")


def next_if(
        tokens: list[TokenType],
        condition: ast.expr
        ) -> tuple[list[TokenType], IfBlock]:
    ...


def next_for(
        tokens: list[TokenType],
        variable: ast.Name,
        iterable: ast.expr
        ) -> tuple[list[TokenType], ForBlock]:
    ...

