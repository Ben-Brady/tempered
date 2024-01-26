import tinycss2
from rcssmin import cssmin
from tinycss2.ast import AtRule, Node
import typing_extensions as t


def finalise_css(css: str) -> str:
    css = minify_css(css)
    css = place_font_imports_at_start(css)
    return css


def place_font_imports_at_start(css: str) -> str:
    rules: t.List[Node] = tinycss2.parse_stylesheet(css)

    def sort_rules(rule: Node) -> int:
        if isinstance(rule, AtRule):
            if rule.at_keyword == "charset":
                return 1
            if rule.at_keyword == "import":
                return 2

        return -1

    rules.sort(key=sort_rules, reverse=True)
    css = tinycss2.serialize(rules)
    return css


def minify_css(css: str) -> str:
    minified_css = cssmin(css)
    if isinstance(minified_css, str):
        return minified_css
    elif isinstance(minified_css, (bytes, bytearray)):
        return minified_css.decode()
    else:
        raise TypeError("Expected str or bytes")
