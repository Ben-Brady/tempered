from . import parse_ast
from typing import TypeAlias, Protocol, runtime_checkable
from dataclasses import dataclass


@runtime_checkable
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


@dataclass
class LayoutToken:
    layout: str


@dataclass
class SlotToken:
    name: str|None
    is_required: bool


@dataclass
class SlotEndToken:
    pass


@dataclass
class BlockToken:
    name: str
    is_required: bool


@dataclass
class BlockEndToken:
    pass


@dataclass
class EscapedExprToken:
    expr: str


@dataclass
class HtmlExprToken:
    expr: str


@dataclass
class ComponentToken:
    call: str


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


@dataclass
class SetToken:
    assignment: str


Token: TypeAlias = (
    LiteralToken |
    ParameterToken | StylesToken | StylesIncludeToken | SetToken |
    ComponentToken | HtmlExprToken | EscapedExprToken |
    IfStartToken | ElIfToken | ElseToken | IfEndToken |
    ForStartToken | ForEndToken |
    LayoutToken | SlotToken | SlotEndToken |BlockToken | BlockEndToken
)
