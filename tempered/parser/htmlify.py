import random
import typing_extensions as t
from . import tags, template_ast
from .scanner import TextScanner

TOKEN_LENGTH = 16


def generate_token_id() -> str:
    def randbytes(length: int):
        return bytes(random.randint(0, 255) for _ in range(length))

    id = randbytes(TOKEN_LENGTH // 2).hex().upper()
    return f"TEMPERED {id}"
    # Must have space before to force it to be quoted


def convert_tags_to_valid_html(
    _tags: t.Sequence[tags.Tag],
) -> t.Tuple[str, t.Dict[str, tags.Tag]]:
    html = ""
    token_lookup: t.Dict[str, tags.Tag] = {}
    for tag in _tags:
        if isinstance(tag, template_ast.HtmlNode):
            html += tag.html
        else:
            token_id = generate_token_id()
            token_lookup[token_id] = tag
            html += token_id

    return html, token_lookup


def convert_tagged_html_to_tokens(
    html: str, token_lookup: t.Dict[str, tags.Tag]
) -> t.Sequence[tags.Tag]:
    TOKEN_ID_LENGTH = len(generate_token_id())

    scanner = TextScanner(html)
    tokens_: t.List[tags.Tag] = []
    while scanner.has_text:
        known_keys = list(token_lookup.keys())
        text = scanner.take_until(known_keys)
        if len(text) > 0:
            tokens_.append(template_ast.HtmlNode(text))

        if not scanner.has_text:
            break

        token_id = scanner.pop_many(TOKEN_ID_LENGTH)
        tokens_.append(token_lookup.pop(token_id))

    return tokens_
