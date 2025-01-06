from pathlib import Path
import typing_extensions as t
from .. import errors
from ..css.extract import extract_css_from_soup
from ..parsing import nodes
from ..parsing.metadata import extract_metadata_from_soup
from ..parsing.parser import parse_soup_into_nodes
from ..utils.minify import minify_html
from ..utils.soup import HtmlSoup
from . import introspection, postprocess


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
    minifed_html = minify_html(html)
    soup = HtmlSoup(minifed_html)
    css = extract_css_from_soup(soup, prefix=name)
    metadata = extract_metadata_from_soup(soup)
    nodes = parse_soup_into_nodes(soup)

    info = introspection.create_template_info(nodes, metadata, css)
    nodes = postprocess.place_default_style_node(nodes, info, css)

    return construct_template_obj(name, file, nodes, css, info)


def construct_template_obj(
    name: str,
    file: t.Optional[Path],
    body: nodes.TemplateBlock,
    css: str,
    info: introspection.TemplateInfo,
) -> nodes.Template:
    if info.is_layout:
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
