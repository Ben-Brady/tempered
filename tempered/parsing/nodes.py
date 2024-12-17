from __future__ import annotations
import ast
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
import typing_extensions as t


class Node(ABC):
    pass


class SingleTagNode(Node):
    pass


@dataclass
class HtmlNode(SingleTagNode):
    html: str


@dataclass
class ExprNode(SingleTagNode):
    value: ast.expr


@dataclass
class RawExprNode(SingleTagNode):
    value: ast.expr


@dataclass
class StyleNode(SingleTagNode):
    """Place styles in component here"""


@dataclass
class ComponentNode(SingleTagNode):
    # Needed to prevent CSS from being created multiple times
    # Also to prevent HTML from being escaped
    component_name: str
    keywords: t.Dict[str, ast.expr]


@dataclass
class AssignmentNode(SingleTagNode):
    target: ast.expr
    value: ast.expr


@dataclass
class ImportNode(SingleTagNode):
    target: str
    name: str


@dataclass
class IfNode(Node):
    condition: ast.expr
    if_block: TemplateBlock
    else_block: t.Optional[TemplateBlock]
    elif_blocks: t.List[t.Tuple[ast.expr, TemplateBlock]] = field(default_factory=list)


@dataclass
class ForNode(Node):
    target: ast.expr
    iterable: ast.expr
    loop_block: TemplateBlock


@dataclass
class SlotNode(Node):
    name: t.Optional[str]
    default: t.Optional[TemplateBlock]


@dataclass
class BlockNode(Node):
    name: t.Optional[str]
    body: TemplateBlock


@dataclass
class TemplateParameter:
    name: str
    type: t.Optional[ast.expr] = None
    default: t.Optional[ast.expr] = None


@dataclass
class SlotInfo:
    name: t.Optional[str]
    is_required: bool = False


@dataclass
class Template:
    is_layout = False
    name: str
    file: t.Optional[Path] = None
    body: TemplateBlock = field(default_factory=list)
    css: str = ""

    parameters: t.List[TemplateParameter] = field(default_factory=list)
    imports: t.List[ImportNode] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)
    layout: t.Union[str, None] = None

    components_calls: t.List[ComponentNode] = field(default_factory=list)
    blocks: t.Set[str] = field(default_factory=set)


@dataclass
class LayoutTemplate(Template):
    is_layout = True
    has_default_slot: bool = False
    slots: t.List[SlotInfo] = field(default_factory=list)


TemplateBlock: t.TypeAlias = t.Sequence[Node]
