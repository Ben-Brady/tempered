from .. import template_ast, tokens
from ..lexer import *
from .token_scanner import TokenScanner
from .expr import parse_expr
from .rules import take_tags_until
import typing_extensions as t
from dataclasses import dataclass, field


@dataclass
class ParseContext:
    body: template_ast.TemplateBlock = field(default_factory=list)

    is_layout: bool = False
    parameters: t.List[template_ast.TemplateParameter] = field(default_factory=list)
    layout: t.Union[str, None] = None

    has_default_slot: bool = False
    slots: t.List[template_ast.SlotTag] = field(default_factory=list)

    components_calls: t.List[template_ast.ComponentTag] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)
    styles_set: bool = False
    blocks: t.Set[str] = field(default_factory=set)


def parse_token_stream(tokens: t.Sequence[tokens.Token], has_css: bool) -> ParseContext:
    scanner = TokenScanner(tokens)
    ctx = ParseContext()
    ctx.body = take_tags_until(ctx, scanner)

    if not ctx.styles_set:
        has_children = len(ctx.style_includes) > 0 or len(ctx.components_calls) > 0
        if ctx.is_layout or has_css or has_children:
            ctx.body = [*ctx.body, template_ast.StyleTag()]

    return ctx
