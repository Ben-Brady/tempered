from ..parser import tokens
from ..parser.text_scanner import TextScanner
from typing import Sequence
import random
from minify_html import minify


def minify_html(html: str) -> str:
    return minify(
        html,
        minify_js=True,
        do_not_minify_doctype=True,
        ensure_spec_compliant_unquoted_attribute_values=True,
        keep_spaces_between_attributes=True,
    )


TOKEN_LENGTH = 16
TOKEN_REGEX = rf"\ TEMPERED_[A-Z0-9]{{{TOKEN_LENGTH}}}"
def generate_token_id() -> str:
    id = random.randbytes(TOKEN_LENGTH // 2).hex().upper()
    return f"TEMPERED {id}"
    # Must have space before to force it to be quoted


def convert_tokens_to_valid_html(
    _tokens: Sequence[tokens.Token],
) -> tuple[str, dict[str, tokens.Token]]:
    html = ""
    token_lookup: dict[str, tokens.Token] = {}
    for token in _tokens:
        match token:
            case tokens.LiteralToken(body):
                html += body
            case token:
                token_id = generate_token_id()
                token_lookup[token_id] = token
                html += token_id

    return html, token_lookup


def tokenised_html_to_tokens(
    html: str, token_lookup: dict[str, tokens.Token]
) -> Sequence[tokens.Token]:
    TOKEN_ID_LENGTH = len(generate_token_id())

    scanner = TextScanner(html)
    tokens_: list[tokens.Token] = []
    while scanner.has_text:
        known_keys = list(token_lookup.keys())
        text = scanner.take_until(known_keys)
        if len(text) > 0:
            tokens_.append(tokens.LiteralToken(text))

        if not scanner.has_text:
            break

        token_id = scanner.pop_many(TOKEN_ID_LENGTH)
        tokens_.append(token_lookup.pop(token_id))

    return tokens_
