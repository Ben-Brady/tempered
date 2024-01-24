from .. import errors, preprocess
from . import htmlify, lexer, template_ast, tags, tree, introspection
from .tags import parse_tokens_to_tags
from .tree import parse_tags_to_template_ast
from .preprocess import preprocess_html
from .postprocess import postprocess
from .introspection import create_template_info
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
    tags = parse_tokens_to_tags(tokens)
    html, token_lookup = htmlify.convert_tags_to_valid_html(tags)

    # Process HTML
    html, css = preprocess.extract_css_from_html(html, prefix=name)
    html = preprocess_html(html)
    # CSS in minified later

    # Reconvert the HTML back into tokens
    tags = htmlify.convert_tagged_html_to_tokens(html, token_lookup)

    # Parse tokens into a body
    body = parse_tags_to_template_ast(tags)
    info = create_template_info(tags, css)
    body = postprocess(body, info)

    if not info.is_layout:
        return template_ast.Template(
            name=name,
            file=file,
            body=body,
            parameters=info.parameters,
            css=css,
            components_calls=info.components_calls,
            style_includes=info.style_includes,
            layout=info.layout,
            blocks=info.blocks,
        )
    else:
        return template_ast.LayoutTemplate(
            name=name,
            file=file,
            body=body,
            css=css,
            parameters=info.parameters,
            components_calls=info.components_calls,
            style_includes=info.style_includes,
            layout=info.layout,
            blocks=info.blocks,
            slots=info.slots,
            has_default_slot=info.has_default_slot,
        )
