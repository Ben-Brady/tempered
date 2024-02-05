import string
from dataclasses import dataclass
from pathlib import Path
import typing_extensions as t
from .scanner import TextScanner

CONTROL_ESCAPE = r"\{"
EXPR_START = "{{"
EXPR_END = "}}"
STATEMENT_START = "{%"
STATEMENT_END = "%}"
IDENT_LETTERS = (
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "0123456789" "_"
)
WHITESPACE = " \t\n\r\v\f"
IDENT_START = string.ascii_letters + "_"
IDENT_CONTINUE = IDENT_START + string.digits


class Token:
    pass


@dataclass
class StatementStartToken(Token):
    pass


@dataclass
class StatementEndToken(Token):
    pass


@dataclass
class ExprStartToken(Token):
    pass


@dataclass
class ExprEndToken(Token):
    pass


@dataclass
class HtmlToken(Token):
    html: str


@dataclass
class PythonExprToken(Token):
    expr: str


@dataclass
class PythonStmtToken(Token):
    stmt: str


@dataclass
class StringToken(Token):
    string: str


@dataclass
class IdentToken(Token):
    name: str


@dataclass
class KeywordToken(Token):
    keyword: str


def to_token_stream(html: str, file: t.Union[Path, None] = None) -> t.Sequence[Token]:
    scanner = TextScanner(html, file)
    _tokens: t.List[Token] = []
    while scanner.has_text:
        _tokens.extend(next_token(scanner))

    return _tokens


def next_token(scanner: TextScanner) -> t.Iterable[Token]:
    if scanner.startswith(STATEMENT_START):
        yield from next_statement_token(scanner)
    elif scanner.startswith(EXPR_START):
        yield from next_expr_token(scanner)
    else:
        yield from next_html_token(scanner)


def next_expr_token(scanner: TextScanner) -> t.Iterable[Token]:
    yield take_token(scanner, EXPR_START, ExprStartToken)
    take_whitespace(scanner)
    yield take_python_expr(scanner, EXPR_END)
    yield take_token(scanner, EXPR_END, ExprEndToken)


def next_html_token(scanner: TextScanner) -> t.Iterable[Token]:
    body = ""
    while scanner.has_text:
        if scanner.startswith("{") and scanner.startswith_many(
            EXPR_START, STATEMENT_START
        ):
            break

        elif scanner.accept(CONTROL_ESCAPE):
            body += "{"
        else:
            body += scanner.pop()

    yield HtmlToken(body)


def next_statement_token(scanner: TextScanner) -> t.Iterable[Token]:
    yield take_token(scanner, STATEMENT_START, StatementStartToken)
    take_whitespace(scanner)

    keyword = take_ident(scanner)
    yield KeywordToken(keyword)
    take_whitespace(scanner)

    if keyword == "if":  # {% if expr %}
        yield take_python_expr(scanner, STATEMENT_END)
    elif keyword == "elif":  # {% elif expr %}
        yield take_python_expr(scanner, STATEMENT_END)
    elif keyword == "html":  # {% rahtmlw expr %}
        yield take_python_expr(scanner, STATEMENT_END)
    elif keyword == "set":  # {% set name = expr %}
        yield take_ident_token(scanner)
        take_whitespace(scanner)
        yield take_keyword(scanner, "=")
        take_whitespace(scanner)
        yield take_python_expr(scanner, STATEMENT_END)
    elif keyword == "param":  # {% param expr %}
        yield take_python_stmt(scanner, STATEMENT_END)
    elif keyword == "component":  # {% component Comp() %}
        yield take_python_expr(scanner, STATEMENT_END)
    elif keyword == "layout":  # {% layout string %}
        yield take_string_token(scanner)
    elif keyword == "include":  # {% include string %}
        yield take_string_token(scanner)
    elif keyword == "block":  # {% block ident %}
        yield take_ident_token(scanner)
    elif keyword == "import":  # {% import Name from "" %}
        yield take_ident_token(scanner)
        yield take_keyword(scanner, "from")
        yield take_string_token(scanner)
    elif keyword == "for":  # {% for ident_a, ident_b in expr %}
        yield from for_token(scanner)
    elif keyword == "slot":  # {% slot name? required? %}
        yield from slot_token(scanner)
    elif keyword in {"else", "endif", "endfor", "styles", "endslot", "endblock"}:
        pass
    else:
        raise scanner.error(f'Unknown Statement "{keyword}"')

    take_whitespace(scanner)
    yield take_token(scanner, STATEMENT_END, StatementEndToken)


def slot_token(scanner: TextScanner) -> t.Iterable[Token]:
    if scanner.startswith_many(*IDENT_START):
        yield take_ident_token(scanner)

    if scanner.accept("required"):
        yield KeywordToken("required")

    take_whitespace(scanner)


def for_token(scanner: TextScanner) -> t.Iterable[Token]:
    yield take_ident_token(scanner)
    take_whitespace(scanner)
    while scanner.startswith(","):
        yield take_keyword(scanner, ",")
        take_whitespace(scanner)
        yield take_ident_token(scanner)
        take_whitespace(scanner)

    yield take_keyword(scanner, "in")
    yield take_python_expr(scanner, STATEMENT_END)


def take_keyword(scanner: TextScanner, keyword: str) -> Token:
    scanner.expect(keyword)
    take_whitespace(scanner)
    return KeywordToken(keyword)


def take_whitespace(scanner: TextScanner):
    scanner.take_while(*WHITESPACE)


def take_python_expr(scanner: TextScanner, *stop_tokens: str) -> Token:
    expr = scanner.take_until(stop_tokens).rstrip()
    take_whitespace(scanner)
    return PythonExprToken(expr)


def take_python_stmt(scanner: TextScanner, *stop_tokens: str) -> Token:
    expr = scanner.take_until(stop_tokens).rstrip()
    take_whitespace(scanner)
    return PythonStmtToken(expr)


def take_token(
    scanner: TextScanner,
    matches: t.Union[str, t.Sequence[str]],
    token: t.Type[Token],
) -> Token:
    if isinstance(matches, str):
        matches = [matches]

    scanner.expect(*matches)
    return token()


def take_ident_token(scanner: TextScanner) -> Token:
    ident = take_ident(scanner)
    take_whitespace(scanner)
    return IdentToken(ident)


def take_ident(scanner: TextScanner) -> str:
    ident = scanner.take(*IDENT_START)
    ident += scanner.take_while(*IDENT_CONTINUE)
    return ident


def take_string_token(scanner: TextScanner) -> Token:
    TERMINATORS = ("'", '"')

    terminator = scanner.take(*TERMINATORS)
    string = ""

    while scanner.has_text:
        if scanner.startswith("\n"):
            raise scanner.error("Newline in the middle of the string")

        if scanner.startswith("\\\\"):
            string += "\\"
        elif scanner.startswith(terminator):
            scanner.expect(terminator)
            take_whitespace(scanner)
            return StringToken(string)
        else:
            string += scanner.pop()

    raise scanner.error("String was not closed")
