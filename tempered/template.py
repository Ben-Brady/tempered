from __future__ import annotations
from dataclasses import dataclass
from ast import expr
from bs4 import BeautifulSoup
from typing import Any, TypeAlias

@dataclass
class BlockLiteral:
    body: str


@dataclass
class BlockStyle:
    is_global: bool
    css: str


@dataclass
class BlockExpr:
    value: expr


@dataclass
class BlockIf:
    condition: expr
    if_block: TemplateBlock
    else_block: TemplateBlock | None


@dataclass
class BlockFor:
    iterable: expr
    loop_variable: expr
    loop_block: TemplateBlock


class RequiredParameter:
    pass


@dataclass
class TemplateParameter:
    name: str
    type: str | None = None
    default: Any | RequiredParameter = RequiredParameter()


@dataclass
class Template:
    name: str
    body: TemplateBlock
    parameters: list[TemplateParameter]
    context: dict[str, Any]


TemplateTag: TypeAlias = BlockLiteral | BlockStyle | BlockExpr | BlockIf | BlockFor
TemplateBlock: TypeAlias = list[TemplateTag]
