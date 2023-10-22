from tempered.parser import *
from bs4 import BeautifulSoup, Tag
import tinycss2
from tinycss2.ast import QualifiedRule, IdentToken, LiteralToken
from rcssmin import cssmin
from typing import cast, LiteralString
from zlib import crc32

import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


html, css = str, str
def preprocess_style_tags(body: str) -> tuple[html, css]:
    soup = BeautifulSoup(body, "html.parser")
    css = ""

    style_tags = cast(list[Tag], soup.find_all("style"))
    for tag in style_tags:
        is_global = tag.has_attr("global")

        if is_global:
            css += tag.text
        else:
            scope_id = _generate_scoped_style_id()
            apply_scope_to_soup(scope_id, soup)
            css += add_scope_rules_to_css(scope_id, tag.text)

        tag.decompose()

    return soup.prettify(formatter="minimal"), minify_css(css)


counter = 0
def _generate_scoped_style_id() -> str:
    global counter
    counter += 1
    id = str(counter).encode()
    hash = hex(crc32(id))[2:]
    return f"tempered-{hash}"


def minify_css(in_css: str) -> str:
    css = cssmin(in_css)
    match css:
        case str():
            return cast(LiteralString, css)
        case bytes() | bytearray():
            return cast(LiteralString, css.decode())
        case _:
            raise TypeError("Expected str or bytes")


def add_scope_rules_to_css(scope_id: str, css: str) -> str:
    css_tokens = tinycss2.parse_stylesheet(css)

    for token in css_tokens:
        if isinstance(token, QualifiedRule):
            token.prelude.insert(0, LiteralToken(0, 0, "."))
            token.prelude.insert(1, IdentToken(0, 0, scope_id))

    return tinycss2.serialize(css_tokens)


def apply_scope_to_soup(scope_id: str, soup: BeautifulSoup):
    for tag in soup.find_all():
        tag: Tag
        class_attr = tag.attrs.get("class", "")
        tag.attrs["class"] = class_attr + f"{scope_id}"
