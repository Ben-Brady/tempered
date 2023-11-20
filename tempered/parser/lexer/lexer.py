from .tokens import *
from .text_scanner import TextScanner
from typing import Sequence
import string


CONTROL_ESCAPE = r"\{"
EXPR_START = "{{"
EXPR_END = "}}"
DIRECTIVE_START = "{!"
DIRECTIVE_END = "!}"
STATEMENT_START = "{%"
STATEMENT_END = "%}"
COMPONENT_START = "{<"
COMPONENT_END = ">}"
IDENT_LETTERS = list(string.ascii_letters + string.digits + "_")
WHITESPACE = string.whitespace


def to_token_stream(html: str) -> Sequence[Token]:
    scanner = TextScanner(html)
    tokens: list[Token] = []
    while scanner.has_text:
        token = take_token(scanner)
        tokens.append(token)

    return tokens


def take_token(scanner: TextScanner) -> Token:
    if scanner.startswith(EXPR_START):
        return take_expr_token(scanner)
    elif scanner.startswith(DIRECTIVE_START):
        return take_directive_token(scanner)
    elif scanner.startswith(STATEMENT_START):
        return take_statement_token(scanner)
    elif scanner.startswith(COMPONENT_START):
        return take_component_token(scanner)
    else:
        return take_literal_token(scanner)


def take_directive_token(scanner: TextScanner) -> Token:
    scanner.checkpoint()
    scanner.expect(DIRECTIVE_START)
    take_whitespace(scanner)
    directive = take_ident(scanner)
    scanner.backtrack()

    match directive:
        case "param":
            return take_param_token(scanner)
        case "styles":
            return take_styles_token(scanner)
        case "include":
            return take_include_token(scanner)
        case "extends":
            return take_extends_token(scanner)
        case _:
            raise scanner.error(f'Unknown Directive "{directive}"')


def take_statement_token(scanner: TextScanner) -> Token:
    scanner.checkpoint()
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    statement = take_ident(scanner)
    scanner.backtrack()

    match statement:
        case "if":
            return take_if_token(scanner)
        case "elif":
            return take_elif_token(scanner)
        case "else":
            return take_else_token(scanner)
        case "endif":
            return take_endif_token(scanner)
        case "for":
            return take_forstart_token(scanner)
        case "endfor":
            return take_forend_token(scanner)
        case "set":
            return take_set_token(scanner)
        case "html":
            return take_html_token(scanner)
        case "slot":
            return take_slot_token(scanner)
        case _:
            raise scanner.error(f'Unknown Statement "{statement}"')


def take_styles_token(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    take_whitespace(scanner)
    scanner.expect("styles")
    take_whitespace(scanner)
    scanner.expect(DIRECTIVE_END)
    return StylesToken()


def take_include_token(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    take_whitespace(scanner)
    scanner.expect("include")
    take_whitespace(scanner)
    template = take_ident(scanner)
    take_whitespace(scanner)
    scanner.expect(DIRECTIVE_END)

    if len(template) == 0:
        raise scanner.error("Template Name cannot be empty")

    return StylesIncludeToken(template)


def take_param_token(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    take_whitespace(scanner)
    scanner.expect("param")

    take_whitespace(scanner)
    parameter = scanner.take_until(DIRECTIVE_END).rstrip()
    take_whitespace(scanner)

    scanner.expect(DIRECTIVE_END)
    return ParameterToken(parameter)


def take_literal_token(scanner: TextScanner) -> LiteralToken:
    body = ""
    while scanner.has_text:
        if scanner.startswith(EXPR_START, DIRECTIVE_START, STATEMENT_START):
            break
        elif scanner.accept(CONTROL_ESCAPE):
            body += "{"
        else:
            body += scanner.pop()

    return LiteralToken(body)


def take_expr_token(scanner: TextScanner) -> EscapedExprToken:
    scanner.expect(EXPR_START)
    take_whitespace(scanner)
    expr = scanner.take_until(EXPR_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(EXPR_END)
    return EscapedExprToken(expr)


def take_html_token(scanner: TextScanner) -> HtmlExprToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("html")
    take_whitespace(scanner)
    expr = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)
    return HtmlExprToken(expr)


def take_component_token(scanner: TextScanner) -> ComponentToken:
    scanner.expect(COMPONENT_START)
    take_whitespace(scanner)
    call = scanner.take_until(COMPONENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(COMPONENT_END)

    return ComponentToken(call)


def take_extends_token(scanner: TextScanner) -> ExtendsToken:
    scanner.expect(DIRECTIVE_START)
    take_whitespace(scanner)
    scanner.expect("extends")
    take_whitespace(scanner)
    layout = take_string(scanner)
    take_whitespace(scanner)
    scanner.expect(DIRECTIVE_END)

    return ExtendsToken(layout)


def take_slot_token(scanner: TextScanner) -> SlotToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("slot")
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return SlotToken(None)


def take_set_token(scanner: TextScanner) -> SetToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("set")
    take_whitespace(scanner)
    assignment = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return SetToken(assignment)


def take_if_token(scanner: TextScanner) -> IfStartToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("if")
    take_whitespace(scanner)
    condition = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return IfStartToken(condition)


def take_elif_token(scanner: TextScanner) -> ElIfToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("elif")
    take_whitespace(scanner)
    condition = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return ElIfToken(condition)


def take_else_token(scanner: TextScanner) -> ElseToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("else")
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)
    return ElseToken()


def take_endif_token(scanner: TextScanner) -> IfEndToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("endif")
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)
    return IfEndToken()


def take_forstart_token(scanner: TextScanner) -> ForStartToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("for")
    take_whitespace(scanner)
    loop_var = take_ident(scanner)
    take_whitespace(scanner)
    scanner.expect("in")
    take_whitespace(scanner)
    iterable = scanner.take_until(STATEMENT_END).rstrip()
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return ForStartToken(variable=loop_var, iterable=iterable)


def take_forend_token(scanner: TextScanner) -> ForEndToken:
    scanner.expect(STATEMENT_START)
    take_whitespace(scanner)
    scanner.expect("endfor")
    take_whitespace(scanner)
    scanner.expect(STATEMENT_END)

    return ForEndToken()


def take_whitespace(scanner: TextScanner):
    WHITESPACE_CHARS = list(string.whitespace)
    scanner.take_while(*WHITESPACE_CHARS)


def take_ident(scanner: TextScanner) -> str:
    return scanner.take_while(*IDENT_LETTERS)


def take_value(scanner: TextScanner) -> str:
    stack = []
    text = ""

    while len(stack) != 0:
        if scanner.accept("None"):
            text += "None"
        elif scanner.accept("True"):
            text += "True"
        elif scanner.accept("False"):
            text += "False"
        elif scanner.startswith("'", '"'):
            return take_string(scanner)
        elif scanner.startswith(*string.digits):
            return take_number(scanner)
        elif scanner.startswith(*IDENT_LETTERS):
            return take_ident(scanner)
        elif scanner.startswith("{", "[", "("):
            char = scanner.pop()
            stack.append(char)
            text += char
        elif scanner.startswith("}", "]", ")"):
            stack.pop()
            text += scanner.pop()

        if not scanner.has_text:
            break

    return text


def take_string(scanner: TextScanner) -> str:
    text = ""

    if scanner.startswith("\"", "\'"):
        string_type = scanner.pop(1)
    elif scanner.startswith("\"\"\"", "\'\'\'"):
        string_type = scanner.pop(3)
    else:
        raise RuntimeError("String must start with ' or \"")

    while scanner.has_text:
        if scanner.startswith(string_type):
            scanner.pop()
            return text

        if scanner.startswith("\\"):
            scanner.pop()

        text += scanner.pop()

    raise scanner.error("String was not closed")


def take_number(scanner: TextScanner) -> str:
    return scanner.take_while(*"0123456789._ox")
