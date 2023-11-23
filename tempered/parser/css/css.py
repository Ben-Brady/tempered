from .scope import apply_scope_to_css
from ... import errors
import bs4
from rcssmin import cssmin
from zlib import crc32
import sass
from typing_extensions import cast, NamedTuple

import warnings
from bs4 import MarkupResemblesLocatorWarning

warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


class ScopedStyles(NamedTuple):
    html: str
    css: str


def tranform_css(body: str, prefix: str = "tempered") -> ScopedStyles:
    soup = bs4.BeautifulSoup(body, "html.parser")
    styles = ""

    style_tags = cast(list[bs4.Tag], soup.find_all("style"))
    for tag in style_tags:
        scope = _generate_scoped_style_id(prefix)
        apply_scope_to_soup(soup, scope)

        css = tag.text
        is_global = tag.has_attr("global")
        lang = tag.get("lang", None)
        if isinstance(lang, list):
            lang = lang[0]

        # Remove shared indent from being in a <style> tag
        try:
            css = transform_css(css, scope, is_global, lang)
        except Exception as e:
            warnings.warn(message="Failed to parse CSS", category=errors.ParsingWarning)
            css = ""

        styles += css
        tag.decompose()

    return ScopedStyles(
        html=soup.prettify(formatter="minimal"),
        css=minify_css(styles),
    )


def remove_shared_ident(css: str) -> str:
    lines = css.split("\n")
    content_lines = [line for line in lines if not (line.isspace() or line == "")]
    if len(lines) == 0 or len(content_lines) == 0:
        return css

    first_line = content_lines[0]
    first_line_without_indent = first_line.lstrip(" ")
    indent_size = len(first_line) - len(first_line_without_indent)
    if indent_size == 0:
        return css

    for i, line in enumerate(lines):
        if line.isspace() or line == "":
            continue

        indent = line[:indent_size]
        if not indent.isspace():
            print(line)
            return css  # Abort indent

        lines[i] = line[indent_size:]

    return "\n".join(lines)


def transform_css(css: str, scope: str, is_global: bool, lang: str | None) -> str:
    if lang == "scss":
        css = sass.compile(
            string=css,
            output_style="compressed",
            indented=False,  # scss rules
        )
    elif lang == "sass":
        css = remove_shared_ident(css)
        css = sass.compile(
            string=css,
            output_style="compressed",
            indented=True,  # sass rules
        )

    if is_global:
        return css

    css = apply_scope_to_css(css, scope)

    return css


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
            return minified_css
        case bytes() | bytearray():
            return minified_css.decode()
        case _:
            raise TypeError("Expected str or bytes")


def apply_scope_to_soup(soup: bs4.BeautifulSoup, scope_id: str):
    for tag in soup.find_all():
        if is_tag_in_head(tag):
            continue

        classes = tag.attrs.get("class", "")

        if isinstance(classes, list):
            classes = " ".join(classes)

        tag.attrs["class"] = classes + " " + scope_id


def is_tag_in_head(tag: bs4.Tag) -> bool:
    if tag.parent is None:
        return False

    if tag.name == "head" or tag.parent.name == "head":
        return True

    return is_tag_in_head(tag.parent)
