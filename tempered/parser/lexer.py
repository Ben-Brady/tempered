from . import python_utils, tokens
from .text_scanner import TextScanner
import typing_extensions as t
import string
from pathlib import Path


CONTROL_ESCAPE = r"\{"
EXPR_START = "{{"
EXPR_END = "}}"
STATEMENT_START = "{%"
STATEMENT_END = "%}"
COMPONENT_START = "{<"
COMPONENT_END = ">}"
COMPONENT_END_ALTERNATIVE = "/>}"
IDENT_LETTERS = list(string.ascii_letters + string.digits + "_")
WHITESPACE = string.whitespace


def to_token_stream(html: str, file: t.Union[Path, None] = None) -> t.Sequence[tokens.Token]:
    scanner = TextScanner(html, file)
    _tokens: t.List[tokens.Token] = []
    while scanner.has_text:
        token = take_token(scanner)
        _tokens.append(token)

    return _tokens


def take_token(scanner: TextScanner) -> tokens.Token:
    if scanner.startswith(STATEMENT_START):
        return take_statement_token(scanner)
    elif scanner.startswith(EXPR_START):
        return take_expr_token(scanner)
    elif scanner.startswith(COMPONENT_START):
        return take_component_token(scanner)
    else:
        return take_literal_token(scanner)


def take_statement_token(scanner: TextScanner) -> tokens.Token:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    statement = python_utils.take_ident(scanner)
    take_whitespace(scanner)

    if statement == "if":
        return take_if_token(scanner)
    elif statement == "elif":
        return take_elif_token(scanner)
    elif statement == "else":
        scanner.expect(STATEMENT_END)
        return tokens.ElseToken()
    elif statement == "endif":
        scanner.expect(STATEMENT_END)
        return tokens.IfEndToken()
    elif statement == "for":
        return take_forstart_token(scanner)
    elif statement == "endfor":
        scanner.expect(STATEMENT_END)
        return tokens.ForEndToken()
    elif statement == "set":
        return take_set_token(scanner)
    elif statement == "html":
        return take_html_token(scanner)
    elif statement == "param":
        return take_param_token(scanner)
    elif statement == "styles":
        scanner.expect(STATEMENT_END)
        return tokens.StylesToken()
    elif statement == "include":
        return take_include_token(scanner)
    elif statement == "layout":
        return take_layout_token(scanner)
    elif statement == "slot":
        return take_slot_token(scanner)
    elif statement == "endslot":
        scanner.expect(STATEMENT_END)
        return tokens.SlotEndToken()
    elif statement == "block":
        return take_block_token(scanner)
    elif statement == "endblock":
        scanner.expect(STATEMENT_END)
        return tokens.BlockEndToken()
    else:
        raise scanner.error(f'Unknown Statement "{statement}"')



def take_include_token(scanner: TextScanner) -> tokens.Token:
    template = python_utils.take_ident(scanner)
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    if len(template) == 0:
        raise scanner.error("Template Name cannot be empty")

    return tokens.StylesIncludeToken(template)


def take_param_token(scanner: TextScanner) -> tokens.Token:
    parameter = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)

    scanner.expect(STATEMENT_END)
    return tokens.ParameterToken(parameter)


def take_literal_token(scanner: TextScanner) -> tokens.LiteralToken:
    body = ""
    while scanner.has_text:
        if scanner.startswith(EXPR_START, STATEMENT_START, COMPONENT_START):
            break
        elif scanner.accept(CONTROL_ESCAPE):
            body += "{"
        else:
            body += scanner.pop()

    return tokens.LiteralToken(body)


def take_expr_token(scanner: TextScanner) -> tokens.EscapedExprToken:
    scanner.expect(EXPR_START)
    take_whitespace(scanner)
    expr = scanner.take_until(EXPR_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(EXPR_END)
    return tokens.EscapedExprToken(expr)


def take_component_token(scanner: TextScanner) -> tokens.ComponentToken:
    scanner.expect(COMPONENT_START)
    take_whitespace(scanner)
    call = scanner.take_until(
        [COMPONENT_END, COMPONENT_END_ALTERNATIVE]).rstrip()
    take_whitespace(scanner)
    scanner.accept("/")  # For />}
    scanner.expect(COMPONENT_END)

    return tokens.ComponentToken(call)


def take_html_token(scanner: TextScanner) -> tokens.HtmlExprToken:
    expr = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)
    return tokens.HtmlExprToken(expr)



def take_layout_token(scanner: TextScanner) -> tokens.LayoutToken:
    layout = python_utils.take_string(scanner)
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.LayoutToken(layout)


def take_slot_token(scanner: TextScanner) -> tokens.SlotToken:
    if scanner.startswith(*python_utils.IDENT_START):
        name = python_utils.take_ident(scanner)
        take_whitespace(scanner)
    else:
        name = None

    is_required = bool(scanner.take_optional("required"))
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.SlotToken(
        name=name,
        is_required=is_required,
    )


def take_block_token(scanner: TextScanner) -> tokens.BlockToken:
    name = python_utils.take_ident(scanner)
    take_whitespace(scanner)

    is_required = bool(scanner.take_optional("required"))
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.BlockToken(
        name=name,
        is_required=is_required
    )


def take_set_token(scanner: TextScanner) -> tokens.SetToken:
    assignment = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.SetToken(assignment)


def take_if_token(scanner: TextScanner) -> tokens.IfStartToken:
    condition = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.IfStartToken(condition)


def take_elif_token(scanner: TextScanner) -> tokens.ElIfToken:
    condition = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.ElIfToken(condition)


def take_forstart_token(scanner: TextScanner) -> tokens.ForStartToken:
    loop_var = python_utils.take_ident(scanner)
    take_whitespace(scanner)
    scanner.expect("in")
    take_whitespace(scanner)
    iterable = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return tokens.ForStartToken(variable=loop_var, iterable=iterable)


def take_whitespace(scanner: TextScanner):
    WHITESPACE_CHARS = list(string.whitespace)
    scanner.take_while(*WHITESPACE_CHARS)
