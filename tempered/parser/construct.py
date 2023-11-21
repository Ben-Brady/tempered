from . import tokens
from ..preprocess import generate_scoped_styles, minify_html
from .parse_ast import *
from .lexer import to_token_stream
from .text_scanner import TextScanner
from .parse.token_scanner import TokenScanner
from .parse.expr import parse_parameter
from .parse.parser import parse_tokens
from pathlib import Path
from typing import Any, Sequence, cast, Literal
import random
import warnings


def parse_template(
    name: str,
    html: str,
    filepath: Path|None = None,
    context: dict[str, Any] | None = None,
) -> Template:
    context = context or {}

    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = to_token_stream(html, filepath=filepath)
    html, token_lookup = reassmble_html(tokens)

    # Process HTML
    html, css = generate_scoped_styles(html, prefix=name)
    html = minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = reparse_html(html, token_lookup)

    # Parse tokens into a body
    scanner = TokenScanner(tokens)
    ctx = parse_tokens(scanner)

    if ctx.is_layout:
        return LayoutTemplate(
            name=name,
            parameters=ctx.parameters,
            context=context,
            body=ctx.body,
            css=css,
            child_components=ctx.child_components,
            layout=ctx.layout,
            blocks=ctx.blocks,
            slots=ctx.slots,
            has_default_slot=ctx.has_default_slot,
        )
    else:
        return Template(
            name=name,
            parameters=ctx.parameters,
            context=context,
            body=ctx.body,
            css=css,
            child_components=ctx.child_components,
            layout=ctx.layout,
            blocks=ctx.blocks,
        )



def generate_token_id() -> str:
    id = random.randbytes(32).hex().upper()
    return f"TEMPEREDED_{id}"


def reassmble_html(
    _tokens: Sequence[tokens.Token]
    ) -> tuple[str, dict[str, tokens.Token]]:
    html = ""
    token_lookup: dict[str, tokens.Token] = {}
    for token in _tokens:
        match token:
            case tokens.LiteralToken(body):
                html += body
            case token:
                token_id = generate_token_id()
                token_lookup[token_id] = token
                html += token_id

    return html, token_lookup


def reparse_html(
    html: str,
    token_lookup: dict[str, tokens.Token]
) -> Sequence[tokens.Token]:
    TOKEN_ID_LENGTH = len(generate_token_id())

    scanner = TextScanner(html)
    tokens_: list[tokens.Token] = []
    while scanner.has_text:
        known_keys = list(token_lookup.keys())
        text = scanner.take_until(known_keys)
        if len(text) > 0:
            tokens_.append(tokens.LiteralToken(text))

        if not scanner.has_text:
            break

        token_id = scanner.pop(TOKEN_ID_LENGTH)
        tokens_.append(token_lookup.pop(token_id))

    if len(token_lookup) > 0:
        warnings.warn(
            "Some of the custom tags are not used,"
            "this is either caused by HTML commenting a custom tag or a bug in the parser",
            RuntimeWarning,
        )

    return tokens_
