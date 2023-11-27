from ..errors import ParserException
from .css import tranform_css
from . import html_, lexer, parse_ast
from .parse import parse_token_stream
from pathlib import Path


def parse_template(
    name: str,
    html: str,
    filepath: Path | None = None,
) -> parse_ast.Template:
    try:
        return _parse_template(
            name=name,
            html=html,
            filepath=filepath,
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
    filepath: Path | None,
) -> parse_ast.Template:
    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = lexer.to_token_stream(html, filepath=filepath)
    html, token_lookup = html_.convert_tokens_to_valid_html(tokens)

    # Process HTML
    html, css = tranform_css(html, prefix=name)
    html = html_.minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = html_.tokenised_html_to_tokens(html, token_lookup)

    # Parse tokens into a body
    ctx = parse_token_stream(tokens)

    if ctx.is_layout:
        return parse_ast.LayoutTemplate(
            name=name,
            file=filepath,
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
        return parse_ast.Template(
            name=name,
            file=filepath,
            parameters=ctx.parameters,
            body=ctx.body,
            css=css,
            components_calls=ctx.components_calls,
            style_includes=ctx.style_includes,
            layout=ctx.layout,
            blocks=ctx.blocks,
        )
