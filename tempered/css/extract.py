import warnings
from importlib.util import find_spec
import bs4
from bs4 import MarkupResemblesLocatorWarning
import typing_extensions as t
from .. import errors
from . import sass, scoped

warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


lxml_installed = find_spec("lxml") is not None
if lxml_installed:
    html_parser = "lxml"
else:
    html_parser = "html.parser"


html: t.TypeAlias = str
css: t.TypeAlias = str


def extract_css_from_html(body: str, prefix: str = "tempered") -> t.Tuple[html, css]:
    soup = bs4.BeautifulSoup(body, html_parser)
    css = ""

    style_tags = t.cast(t.List[bs4.Tag], soup.find_all("style"))
    has_styles = len(style_tags) != 0
    if not has_styles:
        return body, ""

    scope_id = scoped.generate_scope_id(prefix)
    scoped.apply_scope_to_soup(soup, scope_id)
    for tag in style_tags:
        try:
            css += transform_style_tag(tag, scope_id)
        except Exception as e:
            warnings.warn(
                message="Failed to parse CSS",
                category=errors.ParsingWarning,
            )

        tag.decompose()

    html = soup.decode()
    return html, css


def transform_style_tag(tag: bs4.Tag, scope: str) -> str:
    css = tag.text
    is_global = tag.has_attr("global")
    lang = tag.get("lang", None)
    if isinstance(lang, list):
        lang = lang[0]

    if lang in ("sass", "scss"):
        css = sass.transform_sass(css, lang)

    if is_global:
        return css
    else:
        return scoped.apply_scope_to_css(css, scope)
