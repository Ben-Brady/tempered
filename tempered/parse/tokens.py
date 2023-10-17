from . import parse_ast
from ..ast_utils import create_constant
from typing import TypeAlias, Protocol, runtime_checkable
from dataclasses import dataclass
import ast


class Token(Protocol):
    source: str

    def __str__(self) -> str:
        return self.source


class EasyParseToken(Token, Protocol):
    def into_tag(self) -> parse_ast.TemplateTag:
        ...


class LiteralToken(EasyParseToken):
    source: str
    body: str

    def into_tag(self) ->  parse_ast.LiteralBlock:
        return parse_ast.LiteralBlock(self.body)


@dataclass
class StylesToken(EasyParseToken):
    source: str

    def into_tag(self) ->  parse_ast.StyleBlock:
        return parse_ast.StyleBlock()


@dataclass
class StylesIncludeToken(Token):
    source: str
    template: str
    def into_tag(self) ->  parse_ast.IncludeStyleBlock:
        return parse_ast.IncludeStyleBlock(self.template)


@dataclass
class EscapedExprToken:
    source: str
    value: str


@dataclass
class HtmlExprToken:
    source: str
    value: str


@dataclass
class ParameterToken:
    source: str
    parameter: str


@dataclass
class ComponentToken:
    source: str
    body: str


@dataclass
class IfStartToken:
    source: str
    condition: ast.expr


@dataclass
class ElseToken:
    source: str = "{% else %}"
    pass


@dataclass
class IfEndToken:
    pass


@dataclass
class ForStart:
    variable: ast.Name
    iterable: ast.expr


@dataclass
class ForEnd:
    pass


TokenType: TypeAlias = (
    LiteralToken |
    ParameterToken | StylesToken | StylesIncludeToken |
    ComponentToken | HtmlExprToken | EscapedExprToken |
    IfStartToken | ElseToken | IfEndToken |
    ForStart | ForEnd
)


def to_token_stream(html: str) -> list[TokenType]:
    return [
        EscapedExprToken(value=create_constant(html))
    ]
