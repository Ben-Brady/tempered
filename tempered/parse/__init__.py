from ..template import Template, BlockLiteral, BlockStyle
from .tags import parse_parameters
import bs4
from typing import LiteralString, Any, cast
from copy import deepcopy
import minify_html

def parse_template(
        name: str,
        template: LiteralString,
        context: dict[str, Any]
        ) -> Template:
    soup = bs4.BeautifulSoup(template, "html.parser")
    params = parse_parameters(soup)
    template = cast(LiteralString, minify_html.minify(
        template,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    ))

    style_tags = []
    tags: list[bs4.BeautifulSoup] = soup.findChildren("style")
    for tag in tags:
        style_tags.append(BlockStyle(
            is_global=tag.has_attr("global"),
            css=tag.text,
        ))
        tag.decompose()

    return Template(
        name=name,
        parameters=params,
        context=context,
        body=[
            *style_tags,
            BlockLiteral(str(soup))
        ]
    )

