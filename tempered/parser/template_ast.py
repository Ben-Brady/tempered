from __future__ import annotations
from dataclasses import dataclass, field
import ast
from typing import TypeAlias, Sequence
from pathlib import Path
from abc import ABC


class Tag(ABC):
    pass


@dataclass
class LiteralTag(Tag):
    body: str


@dataclass
class ExprTag(Tag):
    value: ast.expr


@dataclass
class HtmlTag(Tag):
    value: ast.expr


@dataclass
class StyleTag(Tag):
    """Place styles in component here"""


@dataclass
class ComponentTag(Tag):
    # Needed to prevent CSS from being created multiple times
    # Also to prevent HTML from being escaped
    component_name: str
    keywords: dict[str, ast.expr]


@dataclass
class IfTag(Tag):
    condition: ast.expr
    if_block: TemplateBlock
    else_block: TemplateBlock | None
    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = field(default_factory=list)


@dataclass
class ForTag(Tag):
    iterable: ast.expr
    loop_variable: ast.Name
    loop_block: TemplateBlock


@dataclass
class AssignmentTag(Tag):
    target: ast.expr
    value: ast.expr


@dataclass
class SlotTag(Tag):
    name: str | None
    default: TemplateBlock | None


@dataclass
class BlockTag(Tag):
    name: str | None
    body: TemplateBlock


TemplateTag: TypeAlias = (
    LiteralTag
    | HtmlTag
    | ExprTag
    | ComponentTag
    | StyleTag
    | IfTag
    | ForTag
    | AssignmentTag
    | SlotTag
    | BlockTag
)


@dataclass
class TemplateParameter:
    name: str
    type: ast.expr | None = None
    default: ast.expr | None = None


@dataclass
class Template:
    name: str
    is_layout = False
    file: Path|None = None
    parameters: list[TemplateParameter] = field(default_factory=list)

    body: TemplateBlock = field(default_factory=list)
    css: str = ""
    layout: str|None = None
    components_calls: list[ComponentTag] = field(default_factory=list)
    style_includes: set[str] = field(default_factory=set)

    blocks: set[str] = field(default_factory=set)


@dataclass
class LayoutTemplate(Template):
    is_layout = True
    has_default_slot: bool = False
    slots: list[SlotTag] = field(default_factory=list)


TemplateBlock: TypeAlias = Sequence[TemplateTag]
