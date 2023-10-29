from ...preprocess import generate_scoped_styles, minify_html
from ..parse_ast import *
from ..lexer import *
from .scanner import TokenScanner
from .expr import parse_parameter
from .parser import create_body
from typing import LiteralString, Any, Sequence


def parse_template(
        name: str,
        template_html: LiteralString,
        context: dict[str, Any]|None = None
        ) -> Template:
    context = context or {}

    html = template_html
    html, css = generate_scoped_styles(html, prefix=name)
    html = minify_html(html)
    tokens = to_token_stream(html)

    tokens, parameters = extract_parameters(tokens)

    scanner = TokenScanner(tokens)
    child_components = get_child_components(tokens)
    body = create_body(scanner)
    body = add_default_style_block(body, child_components, css)

    return Template(
        name=name,
        context=context,
        parameters=parameters,
        body=body,
        child_components=child_components,
        css=css,
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


def add_default_style_block(
        body: TemplateBlock,
        child_components: list[str],
        css: str
        ):
    template_style_tag_count = len([t for t in body if isinstance(t, StyleBlock)])
    if template_style_tag_count > 1:
        raise ValueError("Templates can only have one style block")

    has_styles = css != "" or len(child_components) > 0
    if template_style_tag_count == 0 and has_styles:
        return [*body, StyleBlock()]
    else:
        return body
