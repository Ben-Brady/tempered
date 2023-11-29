from .. import cache, errors
from .css import extract_css
from . import html_, lexer, parse_ast
from .parse import parse_token_stream
from pathlib import Path


def parse_template(
    name: str,
    html: str,
    filepath: Path | None = None,
) -> parse_ast.Template:
    try:
        cached = cache.get_parse_cache(html)
        if cached:
            return cached

        template = _parse_template(
            name=name,
            html=html,
            filepath=filepath,
        )
        cache.set_parse_cache(html, template)
        return template
    except errors.ParserException as e:
        raise e
    except Exception as e:
        msg = f"Failed to parse template {name}"
        if filepath:
            msg += f" in {filepath}"

        raise errors.ParserException(msg) from e


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
    html, css = extract_css(html, prefix=name)
    html = html_.minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = html_.tokenised_html_to_tokens(html, token_lookup)

    # Parse tokens into a body
    ctx = parse_token_stream(tokens, has_css=len(css) > 0)

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
