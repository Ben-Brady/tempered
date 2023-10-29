import tinycss2
from tinycss2.ast import QualifiedRule, IdentToken, LiteralToken


# https://geoffrich.net/posts/svelte-scoped-styles/
def apply_scope_to_css(css: str, scope_id: str) -> str:
    css_tokens = tinycss2.parse_stylesheet(css)
    for token in css_tokens:
        if isinstance(token, QualifiedRule):
            add_scope_to_rule(token, scope_id)

    return tinycss2.serialize(css_tokens)


def add_scope_to_rule(rule: QualifiedRule, scope_id: str):
    for token in list(rule.prelude):
        if isinstance(token, IdentToken):
            insert_scope(rule, scope_id, rule.prelude.index(token))


def insert_scope(rule: QualifiedRule, scope_id: str, position: int):
    rule.prelude.insert(position + 1, IdentToken(0, 0, scope_id))
    rule.prelude.insert(position + 1, LiteralToken(0, 0, "."))
