from .. import parse_ast
from typing import TypeAlias, Protocol
from dataclasses import dataclass
import ast


class EasyParseToken(Protocol):
    def into_tag(self) -> parse_ast.TemplateTag:
        ...


@dataclass
class LiteralToken(EasyParseToken):
    body: str

    def into_tag(self) -> parse_ast.LiteralBlock:
        return parse_ast.LiteralBlock(self.body)


@dataclass
class StylesToken(EasyParseToken):
    def into_tag(self) -> parse_ast.StyleBlock:
        return parse_ast.StyleBlock()


@dataclass
class StylesIncludeToken:
    template: str

    def into_tag(self) -> parse_ast.IncludeStyleBlock:
        return parse_ast.IncludeStyleBlock(self.template)


@dataclass
class EscapedExprToken:
    expr: str


@dataclass
class HtmlExprToken:
    expr: str


@dataclass
class ComponentToken:
    template: str
    expr: str


@dataclass
class ParameterToken:
    parameter: str


@dataclass
class IfStartToken:
    condition: str

@dataclass
class ElIfToken:
    condition: str


@dataclass
class ElseToken:
    pass


@dataclass
class IfEndToken:
    pass


@dataclass
class ForStartToken:
    variable: str
    iterable: str


@dataclass
class ForEndToken:
    pass


Token: TypeAlias = (
    LiteralToken |
    ParameterToken | StylesToken | StylesIncludeToken |
    ComponentToken | HtmlExprToken | EscapedExprToken |
    IfStartToken | ElIfToken | ElseToken | IfEndToken |
    ForStartToken | ForEndToken
)

__all__ = [
    "Token", "LiteralToken",
    "ParameterToken", "StylesToken", "StylesIncludeToken",
    "ComponentToken", "HtmlExprToken", "EscapedExprToken",
    "IfStartToken", "ElIfToken", "ElseToken", "IfEndToken",
    "ForStartToken", "ForEndToken",
]
