from dataclasses import dataclass


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
