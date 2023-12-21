from ..preprocess import htmlify, minify_css, minify_html
from .. import errors, preprocess
from . import lexer, template_ast
from .parser import parse_token_stream
from pathlib import Path
import typing_extensions as t


def parse_template(
    name: str,
    html: str,
    file: t.Union[Path, None] = None,
) -> template_ast.Template:
    try:
        return _parse_template(
            name=name,
            html=html,
            file=file,
        )
    except errors.ParserException as e:
        raise e
    except Exception as e:
        msg = f"Failed to parse template {name}"
        if file:
            msg += f" in {file}"

        raise errors.ParserException(msg) from e


def _parse_template(
    name: str,
    html: str,
    file: t.Union[Path, None],
) -> template_ast.Template:
    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = lexer.to_token_stream(html, file=file)
    html, token_lookup = htmlify.convert_tokens_to_valid_html(tokens)

    # Process HTML
    html, css = preprocess.create_scoped_css(html, prefix=name)
    css = minify_css(css)
    html = minify_html(html)

    # Reconvert the HTML back into tokens
    tokens = htmlify.tokenised_html_to_tokens(html, token_lookup)

    # Parse tokens into a body
    ctx = parse_token_stream(tokens, has_css=len(css) > 0)

    if ctx.is_layout:
        return template_ast.LayoutTemplate(
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
        return template_ast.Template(
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
