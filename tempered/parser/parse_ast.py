from __future__ import annotations
from dataclasses import dataclass, field
import ast
from bs4 import BeautifulSoup
from typing import Any, TypeAlias, Sequence, override
from abc import ABC


class Tag(ABC):
    pass

@dataclass
class LiteralBlock(Tag):
    body: str


@dataclass
class ExprBlock(Tag):
    value: ast.expr


@dataclass
class HtmlBlock(Tag):
    value: ast.expr


@dataclass
class StyleBlock(Tag):
    """Place styles in component here"""


@dataclass
class IncludeStyleBlock(Tag):
    """Include a component style's"""
    template: str


@dataclass
class ComponentBlock(Tag):
    # Needed to prevent CSS from being created multiple times
    # Also to prevent HTML from being escaped
    component_name: str
    keywords: dict[str, ast.expr]


@dataclass
class IfBlock(Tag):
    condition: ast.expr
    if_block: TemplateBlock
    else_block: TemplateBlock | None
    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = field(default_factory=list)


@dataclass
class ForBlock(Tag):
    iterable: ast.expr
    loop_variable: ast.expr
    loop_block: TemplateBlock


@dataclass
class AssignmentBlock(Tag):
    target: ast.expr
    value: ast.expr


TemplateTag: TypeAlias = (
    LiteralBlock | HtmlBlock | ExprBlock |
    ComponentBlock | StyleBlock | IncludeStyleBlock |
    IfBlock | ForBlock | AssignmentBlock
)

class RequiredParameter:
    pass


@dataclass
class TemplateParameter:
    name: str
    type: ast.expr | None = None
    default: ast.expr | RequiredParameter = RequiredParameter()


@dataclass
class Template:
    name: str
    parameters: list[TemplateParameter] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    body: TemplateBlock = field(default_factory=list)
    child_components: list[str] = field(default_factory=list)
    css: str = ""


TemplateBlock: TypeAlias = Sequence[TemplateTag]

__all__ = [
    "TemplateBlock", "TemplateTag", "Template", "Tag",
    "IfBlock", "ForBlock", "AssignmentBlock",
    "LiteralBlock", "ExprBlock", "HtmlBlock", "ComponentBlock",
    "TemplateParameter", "RequiredParameter", "StyleBlock", "IncludeStyleBlock"
]
