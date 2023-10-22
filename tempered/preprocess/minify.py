from minify_html import minify
from typing import cast, LiteralString


def minify_html(html: str) -> str:
    return minify(
        html,
        minify_js=True,
        minify_css=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )
