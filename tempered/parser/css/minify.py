from rcssmin import cssmin  # type: ignore


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    match minified_css:
        case str():
            return minified_css
        case bytes() | bytearray():
            return minified_css.decode()
        case _:
            raise TypeError("Expected str or bytes")
