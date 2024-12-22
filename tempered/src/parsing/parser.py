import bs4
import typing_extensions as t
from ..utils.ast_utils import create_expr
from . import nodes

WHEN_TAG = "t:when"
IF_TAG = "t:if"
THEN_TAG = "t:then"
ELSE_TAG = "t:else"
SWITCH_TAG = "t:switch"
CASE_TAG = "t:case"
DEFAULT_TAG = "t:default"
FOR_TAG = "t:for"
STYLES_TAG = "t:styles"


def parse_soup_into_nodes(soup: bs4.Tag) -> t.Sequence[nodes.Node]:
    body = list(iterate_over_tag(soup))
    body = squash_html_nodes(body)
    return body


def iterate_over_tag(soup: bs4.Tag) -> t.Iterable[nodes.Node]:
    for child in soup.children:
        if isinstance(child, bs4.NavigableString):
            yield nodes.HtmlNode(child.text)
            continue

        tag = t.cast(bs4.Tag, child)
        if tag.name.startswith("c:"):
            name = tag.name.removeprefix("c:")
            yield nodes.ComponentNode(
                component_name=name,
                keywords={
                    key: create_expr(value)
                    for key, value in tag.attrs.items()
                }
            )
        elif tag.name == STYLES_TAG:
            yield nodes.StyleNode()
        elif tag.name == WHEN_TAG:
            condition = create_expr(tag.attrs["condition"])
            yield nodes.IfNode(
                condition=condition,
                if_block=list(parse_soup_into_nodes(tag))
            )
        else:
            yield nodes.HtmlNode(get_opening_tag(tag))
            yield from parse_soup_into_nodes(tag)
            yield nodes.HtmlNode(get_closing_tag(tag))


def squash_html_nodes(_nodes: t.List[nodes.Node]) -> t.List[nodes.Node]:
    "Combined sequential HTML nodes"
    new_nodes = []

    html = ""
    for node in _nodes:
        if isinstance(node, nodes.HtmlNode):
            html += node.html
        else:
            if html:
                new_nodes.append(nodes.HtmlNode(html))
                html = ""

            new_nodes.append(node)


    if html:
        new_nodes.append(nodes.HtmlNode(html))

    return new_nodes


def get_opening_tag(tag: bs4.Tag) -> str:
    raw_attrs = {k: v if not isinstance(v, list) else ' '.join(v) for k, v in tag.attrs.items()}
    attrs = ' '.join((f"{k}=\"{v}\"" for k, v in raw_attrs.items()))
    if not attrs:
        return f"<{tag.name}>"
    else:
        return f"<{tag.name} {attrs}>"


def get_closing_tag(tag: bs4.Tag) -> str:
    return f"</{tag.name}>"
