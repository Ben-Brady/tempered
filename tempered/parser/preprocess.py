from string import whitespace
from minify_html import minify  # type: ignore


def preprocess_html(html: str) -> str:
    html = html.strip(whitespace)
    html = minify_html(html)
    return html


def minify_html(html: str) -> str:
    return minify(
        html,
        minify_js=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )
