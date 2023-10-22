from .tokens import *
from .scanner import TextScanner
from typing import Sequence


EXPR_START = "{{"
EXPR_END = "}}"
DIRECTIVE_START = "{!"
DIRECTIVE_END = "!}"
STATEMENT_START = "{%"
STATEMENT_END = "%}"


def to_token_stream(html: str) -> Sequence[Token]:
    scanner = TextScanner(html)
    tokens: list[Token] = []
    while scanner.has_text:
        token = take_token(scanner)
        tokens.append(token)

    return tokens


def take_token(scanner: TextScanner) -> Token:
    if scanner.startswith(EXPR_START):
        return take_expr(scanner)
    elif scanner.startswith(DIRECTIVE_START):
        return take_directive(scanner)
    elif scanner.startswith(STATEMENT_START):
        return take_statement(scanner)
    else:
        return take_literal(scanner)


def take_directive(scanner: TextScanner) -> Token:
    scanner.checkpoint()
    scanner.expect(DIRECTIVE_START)
    scanner.take_whitespace()
    directive = scanner.take_ident()
    scanner.restore()

    if directive == "param":
        return take_param(scanner)
    elif directive == "styles":
        return take_styles(scanner)
    elif directive == "include":
        return take_include(scanner)
    else:
        raise ValueError(f"Unknown pragma {scanner.html!r}")


def take_statement(scanner: TextScanner) -> Token:
    scanner.checkpoint()
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    statement = scanner.take_ident()
    scanner.restore()

    if statement == "if":
        return take_if(scanner)
    if statement == "elif":
        return take_elif(scanner)
    if statement == "else":
        return take_else(scanner)
    if statement == "endif":
        return take_endif(scanner)
    elif statement == "for":
        return take_forstart(scanner)
    elif statement == "endfor":
        return take_forend(scanner)
    elif statement == "component":
        return take_component(scanner)
    elif statement == "html":
        return take_html(scanner)
    else:
        raise ValueError(f"Unknown pragma")


def take_styles(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    scanner.take_whitespace()
    scanner.expect("styles")
    scanner.take_whitespace()
    scanner.expect(DIRECTIVE_END)
    return StylesToken()


def take_include(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    scanner.take_whitespace()
    scanner.expect("include")
    scanner.take_whitespace()
    template = scanner.take_ident()
    scanner.take_whitespace()
    scanner.expect(DIRECTIVE_END)

    if len(template) == 0:
        raise ValueError("Invalid Template Name: {template!r}")

    return StylesIncludeToken(template)


def take_param(scanner: TextScanner) -> Token:
    scanner.expect(DIRECTIVE_START)
    scanner.take_whitespace()
    scanner.expect("param")
    scanner.take_whitespace()
    parameter = scanner.take_until(DIRECTIVE_END).rstrip()
    scanner.expect(DIRECTIVE_END)
    return ParameterToken(parameter)


def take_literal(scanner: TextScanner) -> LiteralToken:
    body = ""
    while scanner.has_text:
        if scanner.startswith(EXPR_START, DIRECTIVE_START, STATEMENT_START):
            break
        elif scanner.startswith(r"\{"):
            scanner.pop(2)
            body += "{"
        else:
            body += scanner.pop()

    return LiteralToken(body)


def take_expr(scanner: TextScanner) -> EscapedExprToken:
    scanner.expect(EXPR_START)
    expr = scanner.take_until(EXPR_END).strip()
    scanner.expect(EXPR_END)
    return EscapedExprToken(expr)


def take_html(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("html")
    scanner.take_whitespace()
    expr = scanner.take_until(EXPR_END).strip()
    scanner.expect(STATEMENT_END)
    return EscapedExprToken(expr)


def take_component(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("component")
    scanner.take_whitespace()
    scanner.checkpoint()
    template = scanner.take_ident()
    scanner.restore()

    expr = scanner.take_until(STATEMENT_END).strip()
    scanner.expect(STATEMENT_END)

    return ComponentToken(template=template, expr=expr)


def take_if(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("if")
    scanner.take_whitespace()
    condition = scanner.take_until(STATEMENT_END).rstrip()
    scanner.expect(STATEMENT_END)

    return IfStartToken(condition)


def take_elif(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("elif")
    scanner.take_whitespace()
    condition = scanner.take_until(STATEMENT_END).rstrip()
    scanner.take_whitespace()
    scanner.expect(STATEMENT_END)

    return ElIfToken(condition)


def take_else(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("else")
    scanner.take_whitespace()
    scanner.expect(STATEMENT_END)
    return ElseToken()


def take_endif(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("endif")
    scanner.take_whitespace()
    scanner.expect(STATEMENT_END)
    return IfEndToken()


def take_forstart(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("for")
    scanner.take_whitespace()
    loop_var = scanner.take_ident()
    scanner.take_whitespace()
    scanner.expect("in")
    scanner.take_whitespace()
    iterable = scanner.take_until(STATEMENT_END).rstrip()
    scanner.expect(STATEMENT_END)

    return ForStartToken(variable=loop_var, iterable=iterable)


def take_forend(scanner: TextScanner) -> Token:
    scanner.expect(STATEMENT_START)
    scanner.take_whitespace()
    scanner.expect("endfor")
    scanner.take_whitespace()
    scanner.expect(STATEMENT_END)

    return ForEndToken()


