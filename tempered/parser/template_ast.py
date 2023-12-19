from __future__ import annotations
from dataclasses import dataclass, field
import ast
import typing_extensions as t
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
    keywords: t.Dict[str, ast.expr]


@dataclass
class IfTag(Tag):
    condition: ast.expr
    if_block: TemplateBlock
    else_block: t.Union[TemplateBlock, None]
    elif_blocks: t.List[t.Tuple[ast.expr, TemplateBlock]] = field(default_factory=list)


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
    name: t.Union[str, None]
    default: t.Union[TemplateBlock, None]


@dataclass
class BlockTag(Tag):
    name: t.Union[str, None]
    body: TemplateBlock


TemplateTag: t.TypeAlias = t.Union[
    LiteralTag,
    HtmlTag,
    ExprTag,
    ComponentTag,
    StyleTag,
    IfTag,
    ForTag,
    AssignmentTag,
    SlotTag,
    BlockTag,
]


@dataclass
class TemplateParameter:
    name: str
    type: t.Union[ast.expr, None] = None
    default: t.Union[ast.expr, None] = None


@dataclass
class Template:
    name: str
    is_layout = False
    file: t.Union[Path, None] = None
    parameters: t.List[TemplateParameter] = field(default_factory=list)

    body: TemplateBlock = field(default_factory=list)
    css: str = ""
    layout: t.Union[str, None] = None
    components_calls: t.List[ComponentTag] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)

    blocks: t.Set[str] = field(default_factory=set)


@dataclass
class LayoutTemplate(Template):
    is_layout = True
    has_default_slot: bool = False
    slots: t.List[SlotTag] = field(default_factory=list)


TemplateBlock: t.TypeAlias = t.Sequence[TemplateTag]
