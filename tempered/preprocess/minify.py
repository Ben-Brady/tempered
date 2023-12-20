from rcssmin import cssmin
from minify_html import minify


def minify_html(html: str) -> str:
    return minify(
        html,
        minify_js=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    if isinstance(minified_css, str):
        return minified_css
    elif isinstance(minified_css, (bytes, bytearray)):
        return minified_css.decode()
    else:
        raise TypeError("Expected str or bytes")
