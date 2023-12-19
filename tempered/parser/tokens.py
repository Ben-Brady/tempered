from . import template_ast
import typing_extensions as t
from dataclasses import dataclass


@t.runtime_checkable
class EasyParseToken(t.Protocol):
    def into_tag(self) -> template_ast.TemplateTag:
        ...


@dataclass
class LiteralToken(EasyParseToken):
    body: str

    def into_tag(self) -> template_ast.LiteralTag:
        return template_ast.LiteralTag(self.body)


@dataclass
class StylesToken(EasyParseToken):
    def into_tag(self) -> template_ast.StyleTag:
        return template_ast.StyleTag()


@dataclass
class StylesIncludeToken:
    template: str


@dataclass
class LayoutToken:
    layout: str


@dataclass
class SlotToken:
    name: t.Union[str, None]
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


Token: t.TypeAlias = t.Union[
    LiteralToken, ParameterToken, StylesToken,  StylesIncludeToken,
    SetToken, ComponentToken, HtmlExprToken,  EscapedExprToken,
    ForStartToken, ForEndToken, IfStartToken, ElIfToken, ElseToken,
    IfEndToken, LayoutToken, SlotToken,  SlotEndToken, BlockToken, BlockEndToken
]
