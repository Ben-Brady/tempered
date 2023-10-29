from tempered.parser import *
from .scope import apply_scope_to_css
from bs4 import BeautifulSoup, Tag
from tinycss2.ast import QualifiedRule, IdentToken, LiteralToken
from rcssmin import cssmin
from typing import cast, LiteralString, NamedTuple
from zlib import crc32

import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


class ScopedStyles(NamedTuple):
    html: str
    css: str


def generate_scoped_styles(body: str, prefix: str = "tempered") -> ScopedStyles:
    soup = BeautifulSoup(body, "html.parser")
    css = ""

    style_tags = cast(list[Tag], soup.find_all("style"))
    for tag in style_tags:
        is_global = tag.has_attr("global")

        if is_global:
            css += tag.text
        else:
            scope_id = _generate_scoped_style_id(prefix)
            apply_scope_to_soup(soup, scope_id)
            css += apply_scope_to_css(tag.text, scope_id)

        tag.decompose()

    return ScopedStyles(
        html=soup.prettify(formatter="minimal"),
        css=minify_css(css)
    )


counter = 0
def _generate_scoped_style_id(prefix: str) -> str:
    global counter
    counter += 1
    id = str(counter).encode()

    prefix = prefix.replace("-", "_").lower()
    hash = hex(crc32(id))[2:6]
    return f"{prefix}-{hash}"


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    match minified_css:
        case str():
            return cast(LiteralString, minified_css)
        case bytes() | bytearray():
            return cast(LiteralString, minified_css.decode())
        case _:
            raise TypeError("Expected str or bytes")


def apply_scope_to_soup(soup: BeautifulSoup, scope_id: str):
    for tag in soup.find_all():
        tag: Tag
        classes = tag.attrs.get("class", "")

        if isinstance(classes, list):
            classes = " ".join(classes)

        tag.attrs["class"] = classes + " " + scope_id
