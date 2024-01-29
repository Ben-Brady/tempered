from string import whitespace
from minify_html import minify  # type: ignore


def minify_html(html: str) -> str:
    html = minify(
        html,
        minify_js=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )
    html = html.strip(whitespace)
    return html
