from . import sass, scoped
from ... import errors
import bs4
from rcssmin import cssmin
from typing_extensions import cast, NamedTuple
import warnings
from bs4 import MarkupResemblesLocatorWarning

warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


class ExtractedCss(NamedTuple):
    html: str
    css: str


def extract_css(body: str, prefix: str = "tempered") -> ExtractedCss:
    soup = bs4.BeautifulSoup(body, "html.parser")
    styles = ""

    style_tags = cast(list[bs4.Tag], soup.find_all("style"))
    for tag in style_tags:
        scope_id = scoped.generate_scope_id(prefix)
        scoped.apply_scope_to_soup(soup, scope_id)

        try:
            css = tag.text
            is_global = tag.has_attr("global")
            lang = tag.get("lang", None)
            if isinstance(lang, list):
                lang = lang[0]
            css = transform_css(css, scope_id, is_global, lang)
        except Exception:
            warnings.warn(message="Failed to parse CSS", category=errors.ParsingWarning)
            css = ""

        styles += css
        tag.decompose()

    return ExtractedCss(
        html=soup.prettify(formatter="minimal"),
        css=minify_css(styles),
    )


def transform_css(css: str, scope: str, is_global: bool, lang: str | None) -> str:
    if lang == "scss" or lang == "sass":
        css = sass.transform_sass(css, lang)

    if is_global:
        return css
    else:
        return scoped.apply_scope_to_css(css, scope)


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    match minified_css:
        case str():
            return minified_css
        case bytes() | bytearray():
            return minified_css.decode()
        case _:
            raise TypeError("Expected str or bytes")