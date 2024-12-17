from pathlib import Path
import typing_extensions as t


from . import errors
from .parsing import parser

from .lexing import lexer
from .introspection import introspecter
from .utils.minify import minify_html
from .css.extract import extract_css_from_html
from .parsing import htmlify, nodes, postprocess
from .tagbuilding.builder import parse_tokens_to_tags


def parse_template(
    name: str,
    html: str,
    file: t.Union[Path, None] = None,
) -> nodes.Template:
    try:
        return _parse_template(
            name=name,
            html=html,
            file=file,
        )
    except errors.ParserException as e:
        raise e
    except Exception as e:
        if file:
            msg = f"Failed to parse template {name} in {file}"
        else:
            msg = f"Failed to parse template {name}"

        raise errors.ParserException(msg) from e


def _parse_template(
    name: str,
    html: str,
    file: t.Union[Path, None],
) -> nodes.Template:
    # Convert tokens into constant character
    # This is to prevent HTML parsing mangling it
    tokens = lexer.to_token_stream(html, file=file)
    tags = parse_tokens_to_tags(tokens)
    html, token_lookup = htmlify.convert_tags_to_valid_html(tags)

    # Process HTML
    html, css = extract_css_from_html(html, prefix=name)
    html = minify_html(html)
    # Note: CSS in minified later

    # Reconvert the HTML back into tokens
    tags = htmlify.convert_tagged_html_to_tokens(html, token_lookup)
    body = parser.parse_tags_to_template_ast(tags)

    # Postprocessing
    info = introspecter.create_template_info(tags, css)
    body = postprocess.place_default_style_node(body, info, css)

    # Construct the final object
    return construct_template_obj(name, file, body, css, info)


def construct_template_obj(
    name: str,
    file: t.Optional[Path],
    body: nodes.TemplateBlock,
    css: str,
    info: introspecter.TemplateInfo,
) -> nodes.Template:
    if not info.is_layout:
        return nodes.Template(
            name=name,
            file=file,
            body=body,
            parameters=info.parameters,
            css=css,
            components_calls=info.components_calls,
            style_includes=info.style_includes,
            layout=info.layout,
            blocks=info.blocks,
            imports=info.imports,
        )
    else:
        return nodes.LayoutTemplate(
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
            imports=info.imports,
        )
