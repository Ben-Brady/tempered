from typing_extensions import cast, LiteralString
from minify_html import minify
from rcssmin import cssmin  # type: ignore


def minify_html(html: str) -> str:
    return minify(
        html,
        minify_js=True,
        minify_css=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    match minified_css:
        case str():
            return cast(LiteralString, minified_css)
        case bytes() | bytearray():
            return cast(LiteralString, minified_css.decode())
        case _:
            raise TypeError("Expected str or bytes")
