from zlib import crc32
import bs4
import tinycss2
from tinycss2.ast import HashToken, IdentToken, LiteralToken, QualifiedRule
import typing_extensions as t

# QualifiedRule = #a .b {}


# https://geoffrich.net/posts/svelte-scoped-styles/
def apply_scope_to_css(css: str, scope: str) -> str:
    css_tokens = tinycss2.parse_stylesheet(css)
    for token in list(css_tokens):
        if isinstance(token, QualifiedRule):
            add_scope_to_rule(token, scope)

    return tinycss2.serialize(css_tokens)


# QualifiedRule.prelude = #a .b
def add_scope_to_rule(rule: QualifiedRule, scope: str):
    checked_tokens = []

    # Find first scopable rule
    def insert_scope(rule: QualifiedRule, scope: str, position: int):
        scope_ident = IdentToken(0, 0, scope)
        class_token = LiteralToken(0, 0, ".")
        rule.prelude.insert(position + 1, scope_ident)
        rule.prelude.insert(position + 1, class_token)
        checked_tokens.extend((scope_ident, class_token))

    for token in list(rule.prelude):
        checked_tokens.append(token)

        if isinstance(token, (IdentToken, HashToken)):
            insert_scope(rule, scope, rule.prelude.index(token))
            break

    # Find last scopable rule
    for token in reversed(list(rule.prelude)):
        if token in checked_tokens:
            break  # We met in the middle

        if isinstance(token, (IdentToken, HashToken)):
            insert_scope(rule, scope, rule.prelude.index(token))
            break


counter = 0


def generate_scope_id(prefix: t.Union[str, None] = None) -> str:
    global counter
    counter += 1
    id = str(counter).encode()
    hash = hex(crc32(id))[2:]

    if prefix is None:
        return hash
    else:
        prefix = prefix.replace("-", "_").lower()
        return f"{prefix}-{hash[:6]}"


def apply_scope_to_soup(soup: bs4.BeautifulSoup, scope_id: str):
    for tag in soup.find_all():
        if is_tag_in_head(tag):
            continue

        classes = tag.attrs.get("class", "")

        if isinstance(classes, list):
            classes = " ".join(classes)

        tag.attrs["class"] = classes + " " + scope_id


def is_tag_in_head(tag: bs4.Tag) -> bool:
    if tag.parent is None:
        return False

    if tag.name == "head" or tag.parent.name == "head":
        return True

    return is_tag_in_head(tag.parent)
