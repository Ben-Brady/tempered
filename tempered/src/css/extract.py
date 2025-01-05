import warnings

import bs4
from bs4 import MarkupResemblesLocatorWarning
import typing_extensions as t
from dataclasses import dataclass
from .. import errors
from ..utils.soup import HtmlSoup
from . import sass, scoped

warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


@dataclass
class CssOptions:
    is_global: bool
    scope_id: str
    lang: t.Optional[str]


class ExtractResult(t.NamedTuple):
    html: str
    css: str


def extract_css_from_html(body: str, prefix: t.Optional[str] = None) -> ExtractResult:
    soup = HtmlSoup(body)
    css = ""

    style_tags = t.cast(t.List[bs4.Tag], soup.find_all("style"))
    has_styles = len(style_tags) != 0
    if not has_styles:
        return ExtractResult(body, css="")

    scope_id = scoped.generate_scope_id(prefix)
    scoped.apply_scope_to_soup(soup, scope_id)
    for tag in style_tags:
        try:
            options = CssOptions(
                is_global=tag.has_attr("global"),
                scope_id=scope_id,
                lang=get_bs4_attr(tag, "lang")
            )

            css += transform_styles(tag.text, options)
        except Exception:
            warnings.warn(
                message="Failed to parse CSS",
                category=errors.ParsingWarning,
            )

        tag.decompose()

    html = soup.decode()
    return ExtractResult(html, css)


def transform_styles(css: str, options: CssOptions) -> str:
    if options.lang in ("sass", "scss"):
        css = sass.transform_sass(css, options.lang)

    if not options.is_global:
        css = scoped.apply_scope_to_css(css, options.scope_id)

    return css


def get_bs4_attr(tag: bs4.Tag, attr: str) -> t.Optional[str]:
    value = tag.get(attr, None)
    if isinstance(value, list):
        value = value[0]

    return value
