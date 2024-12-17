from __future__ import annotations
import ast
from abc import ABC
from dataclasses import dataclass
from ..parsing.nodes import SingleTagNode
import typing_extensions as t


class CompositeTag(ABC):
    pass


class PragmaTag(ABC):
    pass


@dataclass
class IfStartTag(CompositeTag):
    condition: ast.expr


@dataclass
class ElIfTag(CompositeTag):
    condition: ast.expr


@dataclass
class ElseTag(CompositeTag):
    pass


@dataclass
class IfEndTag(CompositeTag):
    pass


@dataclass
class ForStartTag(CompositeTag):
    iterable: ast.expr
    target: ast.expr


@dataclass
class ForEndTag(CompositeTag):
    pass


@dataclass
class SlotStartTag(CompositeTag):
    name: t.Union[str, None]
    is_required: bool = False


@dataclass
class SlotEndTag(CompositeTag):
    pass


@dataclass
class BlockStartTag(CompositeTag):
    name: str


@dataclass
class BlockEndTag(CompositeTag):
    pass


@dataclass
class LayoutTag(PragmaTag):
    template: str


@dataclass
class IncludeTag(PragmaTag):
    template: str


@dataclass
class ParameterTag(PragmaTag):
    name: str
    type: t.Union[ast.expr, None] = None
    default: t.Union[ast.expr, None] = None


Tag: t.TypeAlias = t.Union[CompositeTag, PragmaTag, SingleTagNode]
