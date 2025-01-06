from dataclasses import dataclass, field
import typing_extensions as t
from ..parsing import nodes
from ..parsing.metadata import Metadata
from ..utils.ast_utils import create_expr


@dataclass
class TemplateInfo:
    css: str
    is_layout: bool = False
    parameters: t.List[nodes.TemplateParameter] = field(default_factory=list)
    layout: t.Union[str, None] = None

    has_default_slot: bool = False
    slots: t.List[nodes.SlotInfo] = field(default_factory=list)

    imports: t.List[nodes.ImportNode] = field(default_factory=list)
    components_calls: t.List[nodes.ComponentNode] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)
    styles_set: bool = False
    blocks: t.Set[str] = field(default_factory=set)


def create_template_info(
    stream: t.Sequence[nodes.Node], metadata: Metadata, css: str
) -> TemplateInfo:
    pragma_rules = [
        (nodes.StyleNode, style_pragma),
        (nodes.ComponentNode, component_prgama),
        (nodes.SlotNode, slot_pragma),
        (nodes.BlockNode, block_pragma),
    ]

    ctx = TemplateInfo(css)

    # TODO: refactor metadata and introspection
    ctx.layout = metadata.layout
    ctx.style_includes = set(metadata.style_includes)
    # TODO: Don't need import node, atrifact from when they were {% import %}
    ctx.imports = [
        nodes.ImportNode(target=name.lower(), name=value)
        for name, value in metadata.imports.items()
    ]

    ctx.parameters = []
    for name, value in metadata.parameters.items():
        if isinstance(value, str):
            type_str = value
            default_str = value
        else:
            type_str = value["type"]
            default_str = value["default"]

        # TODO: Defer create_expr to compiler
        parameter = nodes.TemplateParameter(
            name=name,
            type=create_expr(type_str) if type_str else None,
            default=create_expr(default_str) if default_str else None,
        )
        ctx.parameters.append(parameter)

    for tag in stream:
        for rule_tag, func in pragma_rules:
            if isinstance(tag, rule_tag):
                func(ctx, tag)

    return ctx


def style_pragma(ctx: TemplateInfo, tag: nodes.StyleNode) -> t.Optional[nodes.Node]:
    if ctx.styles_set:
        raise ValueError("Template cannot have multiple styles tags")

    ctx.styles_set = True
    return nodes.StyleNode()


def component_prgama(
    ctx: TemplateInfo, tag: nodes.ComponentNode
) -> t.Optional[nodes.Node]:
    call = nodes.ComponentNode(component_name=tag.component_name, keywords=tag.keywords)
    ctx.components_calls.append(call)
    return call


def slot_pragma(ctx: TemplateInfo, token: nodes.SlotNode) -> None:
    ctx.is_layout = True

    if token.name is None:
        if ctx.has_default_slot:
            raise ValueError("Template cannot have multiple default slots")

        ctx.has_default_slot = True

    slot = nodes.SlotInfo(
        name=token.name,
        is_required=not token.default,
    )
    ctx.slots.append(slot)


def block_pragma(ctx: TemplateInfo, token: nodes.BlockNode) -> None:
    if token.name is not None:
        ctx.blocks.add(token.name)
