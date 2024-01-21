import tinycss2
from tinycss2.ast import Node, AtRule
from ..minify import minify_css
from rcssmin import cssmin
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
