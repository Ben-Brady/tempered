from ..errors import ParserException
from .css import tranform_css, minify_html
from . import tokens
from .parse_ast import *
from .lexer import to_token_stream
from .text_scanner import TextScanner
from .parse import parse_token_stream
from pathlib import Path
from typing import Any, Sequence
import random
import warnings


def parse_template(
    name: str,
    html: str,
    filepath: Path | None = None,
) -> Template:
    try:
        return _parse_template(
            name=name,
            html=html,
            file=filepath,
        )
    except ParserException as e:
        raise e
    except Exception as e:
        msg = f"Failed to parse template {name}"
        if filepath:
            msg += f" in {filepath}"

        raise ParserException(msg) from e


def _parse_template(
    name: str,
    html: str,
    file: Path | None,
) -> Template:
    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = to_token_stream(html, filepath=file)
    html, token_lookup = reassmble_html(tokens)

    # Process HTML
    html, css = tranform_css(html, prefix=name)
    html = minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = reparse_html(html, token_lookup)

    # Parse tokens into a body
    ctx = parse_token_stream(tokens)

    if ctx.is_layout:
        return LayoutTemplate(
            name=name,
            file=file,
            parameters=ctx.parameters,
            body=ctx.body,
            css=css,
            components_calls=ctx.components_calls,
            style_includes=ctx.style_includes,
            layout=ctx.layout,
            blocks=ctx.blocks,
            slots=ctx.slots,
            has_default_slot=ctx.has_default_slot,
        )
    else:
        return Template(
            name=name,
            file=file,
            parameters=ctx.parameters,
            body=ctx.body,
            css=css,
            components_calls=ctx.components_calls,
            style_includes=ctx.style_includes,
            layout=ctx.layout,
            blocks=ctx.blocks,
        )


def generate_token_id() -> str:
    id = random.randbytes(32).hex().upper()
    return f"TEMPEREDED_{id}"


def reassmble_html(
    _tokens: Sequence[tokens.Token],
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
    html: str, token_lookup: dict[str, tokens.Token]
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
