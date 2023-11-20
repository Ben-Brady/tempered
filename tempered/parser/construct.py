from ..preprocess import generate_scoped_styles, minify_html
from .parse_ast import *
from .lexer import *
from .lexer.text_scanner import TextScanner
from .parse.token_scanner import TokenScanner
from .parse.expr import parse_parameter
from .parse.parser import create_body
from typing import Any, Sequence, cast, Literal
import random


def parse_template(
    name: str,
    html: str,
    context: dict[str, Any] | None = None,
) -> Template:
    context = context or {}

    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = to_token_stream(html)
    html, token_lookup = reassmble_html(tokens)

    # Process HTML
    html, css = generate_scoped_styles(html, prefix=name)
    html = minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = reparse_html(html, token_lookup)

    # Token Inferance
    type = get_type(tokens)
    tokens, layout = extract_layout(tokens)
    tokens, parameters = extract_parameters(tokens)
    child_components = get_child_components(tokens)

    # Parse tokens into a body
    scanner = TokenScanner(tokens)
    body = create_body(scanner)
    body = add_default_style_block(body, child_components, css)

    return Template(
        name=name,
        parameters=parameters,
        context=context,
        type=type,

        body=body,
        css=css,
        child_components=list(child_components),
        layout=layout,
    )


def extract_parameters(
    tokens: Sequence[Token],
) -> tuple[Sequence[Token], list[TemplateParameter]]:
    parameters = [
        parse_parameter(token.parameter)
        for token in tokens
        if isinstance(token, ParameterToken)
    ]
    tokens = [token for token in tokens if not isinstance(token, ParameterToken)]
    return tokens, parameters


def get_child_components(tokens: Sequence[Token]) -> Sequence[str]:
    return [token.call for token in tokens if isinstance(token, ComponentToken)]


def add_default_style_block(
    body: TemplateBlock, child_components: Sequence[str], css: str
):
    template_style_tag_count = len([t for t in body if isinstance(t, StyleBlock)])
    if template_style_tag_count > 1:
        raise ValueError("Templates can only have one style block")

    has_styles = css != "" or len(child_components) > 0
    if template_style_tag_count == 0 and has_styles:
        return [*body, StyleBlock()]
    else:
        return body


def extract_layout(tokens: Sequence[Token]) -> tuple[Sequence[Token], str | None]:
    layout_tokens = [t for t in tokens if isinstance(t, ExtendsToken)]
    tokens = [t for t in tokens if not isinstance(t, ExtendsToken)]
    if len(layout_tokens) == 0:
        return tokens, None
    elif len(layout_tokens) == 1:
        return tokens, layout_tokens[0].layout
    else:
        raise ValueError("Templates can only have one slot tag")


def get_type(tokens: Sequence[Token]) -> TemplateType:
    slots =[
        t for t in tokens
        if isinstance(t, SlotToken)
    ]
    if len(slots) > 0:
        return "layout"
    else:
        return "component"


def generate_token_id() -> str:
    id = random.randbytes(32).hex().upper()
    return f"TEMPEREDED_{id}"


def reassmble_html(tokens: Sequence[Token]) -> tuple[str, dict[str, Token]]:
    html = ""
    token_lookup = {}
    for token in tokens:
        match token:
            case LiteralToken(body):
                html += body
            case token:
                token_id = generate_token_id()
                token_lookup[token_id] = token
                html += token_id

    return html, token_lookup


def reparse_html(html: str, token_lookup: dict[str, Token]) -> Sequence[Token]:
    TOKEN_ID_LENGTH = len(generate_token_id())

    scanner = TextScanner(html)
    tokens = []
    while scanner.has_text:
        known_keys = list(token_lookup.keys())
        text = scanner.take_until(known_keys)
        if len(text) > 0:
            tokens.append(LiteralToken(text))

        if not scanner.has_text:
            break

        token_id = scanner.pop(TOKEN_ID_LENGTH)
        tokens.append(token_lookup.pop(token_id))

    if len(token_lookup) > 0:
        raise RuntimeError("Some of the tags were mangled by the HTML")

    return tokens
