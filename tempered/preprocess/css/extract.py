from . import sass, scoped
from ... import errors
import bs4
import typing_extensions as t
import warnings
from bs4 import MarkupResemblesLocatorWarning

warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)


html: t.TypeAlias = str
css: t.TypeAlias = str


def extract_css_from_html(body: str, prefix: str = "tempered") -> t.Tuple[html, css]:
    soup = bs4.BeautifulSoup(body, "html.parser")
    css = ""

    style_tags = t.cast(t.List[bs4.Tag], soup.find_all("style"))
    has_styles = len(style_tags) != 0
    if not has_styles:
        return body, ""

    scope_id = scoped.generate_scope_id(prefix)
    scoped.apply_scope_to_soup(soup, scope_id)
    for tag in style_tags:
        try:
            styles = tag.text
            is_global = tag.has_attr("global")
            lang = tag.get("lang", None)
            if isinstance(lang, list):
                lang = lang[0]
            styles = transform_style_tag(styles, scope_id, is_global, lang)
        except Exception:
            warnings.warn(message="Failed to parse CSS", category=errors.ParsingWarning)
            styles = ""

        css += styles
        tag.decompose()

    html = soup.prettify(formatter="minimal")
    return html, css


def transform_style_tag(
    css: str, scope: str, is_global: bool, lang: t.Union[str, None]
) -> str:
    if lang == "scss" or lang == "sass":
        css = sass.transform_sass(css, lang)

    if is_global:
        return css
    else:
        return scoped.apply_scope_to_css(css, scope)
