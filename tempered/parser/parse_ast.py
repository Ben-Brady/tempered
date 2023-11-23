from __future__ import annotations
from dataclasses import dataclass, field
import ast
from typing import Any, TypeAlias, Sequence, Literal
from pathlib import Path
from abc import ABC


class Block(ABC):
    pass


@dataclass
class LiteralBlock(Block):
    body: str


@dataclass
class ExprBlock(Block):
    value: ast.expr


@dataclass
class HtmlBlock(Block):
    value: ast.expr


@dataclass
class StyleBlock(Block):
    """Place styles in component here"""


@dataclass
class ComponentBlock(Block):
    # Needed to prevent CSS from being created multiple times
    # Also to prevent HTML from being escaped
    component_name: str
    keywords: dict[str, ast.expr]


@dataclass
class IfBlock(Block):
    condition: ast.expr
    if_block: TemplateBlock
    else_block: TemplateBlock | None
    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = field(default_factory=list)


@dataclass
class ForBlock(Block):
    iterable: ast.expr
    loop_variable: ast.expr
    loop_block: TemplateBlock


@dataclass
class AssignmentBlock(Block):
    target: ast.expr
    value: ast.expr


@dataclass
class SlotBlock(Block):
    name: str | None
    default: TemplateBlock | None


@dataclass
class BlockBlock(Block):
    name: str | None
    body: TemplateBlock


TemplateTag: TypeAlias = (
    LiteralBlock
    | HtmlBlock
    | ExprBlock
    | ComponentBlock
    | StyleBlock
    | IfBlock
    | ForBlock
    | AssignmentBlock
    | SlotBlock
    | BlockBlock
)


@dataclass
class TemplateParameter:
    name: str
    type: ast.expr | None = None
    default: ast.expr | None = None


@dataclass
class Template:
    name: str
    file: Path|None = None
    parameters: list[TemplateParameter] = field(default_factory=list)

    body: TemplateBlock = field(default_factory=list)
    css: str = ""
    layout: str|None = None
    components_calls: list[ComponentBlock] = field(default_factory=list)
    style_includes: set[str] = field(default_factory=set)

    blocks: set[str] = field(default_factory=set)


@dataclass
class LayoutTemplate(Template):
    has_default_slot: bool = False
    slots: list[SlotBlock] = field(default_factory=list)


TemplateBlock: TypeAlias = Sequence[TemplateTag]
