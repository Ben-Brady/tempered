from ..parser import tokens
from ..parser.text_scanner import TextScanner
import typing_extensions as t
import random

TOKEN_LENGTH = 16
TOKEN_REGEX = rf"\ TEMPERED_[A-Z0-9]{{{TOKEN_LENGTH}}}"
def generate_token_id() -> str:
    def randbytes(length: int):
        return bytes(random.randint(0, 255) for _ in range(length))

    id = randbytes(TOKEN_LENGTH // 2).hex().upper()
    return f"TEMPERED {id}"
    # Must have space before to force it to be quoted


def convert_tokens_to_valid_html(
    _tokens: t.Sequence[tokens.Token],
) -> t.Tuple[str, t.Dict[str, tokens.Token]]:
    html = ""
    token_lookup: t.Dict[str, tokens.Token] = {}
    for token in _tokens:
        if isinstance(token, tokens.LiteralToken):
            html += token.body
        else:
            token_id = generate_token_id()
            token_lookup[token_id] = token
            html += token_id

    return html, token_lookup


def tokenised_html_to_tokens(
    html: str, token_lookup: t.Dict[str, tokens.Token]
) -> t.Sequence[tokens.Token]:
    TOKEN_ID_LENGTH = len(generate_token_id())

    scanner = TextScanner(html)
    tokens_: t.List[tokens.Token] = []
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
