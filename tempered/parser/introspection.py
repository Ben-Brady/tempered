from dataclasses import dataclass, field
import typing_extensions as t
from . import scanner, tags, template_ast


@dataclass
class TemplateInfo:
    css: str
    is_layout: bool = False
    parameters: t.List[template_ast.TemplateParameter] = field(default_factory=list)
    layout: t.Union[str, None] = None

    has_default_slot: bool = False
    slots: t.List[template_ast.SlotInfo] = field(default_factory=list)

    imports: t.List[template_ast.ImportNode] = field(default_factory=list)
    components_calls: t.List[template_ast.ComponentNode] = field(default_factory=list)
    style_includes: t.Set[str] = field(default_factory=set)
    styles_set: bool = False
    blocks: t.Set[str] = field(default_factory=set)


TagScanner = scanner.Scanner[tags.Tag]
T = t.TypeVar("T", bound=tags.Tag)
ParseRules: t.TypeAlias = t.List[
    t.Tuple[
        t.Type[T],
        t.Callable[[TemplateInfo, T], t.Optional[template_ast.Node]],
    ]
]


def create_template_info(stream: t.Sequence[tags.Tag], css: str) -> TemplateInfo:
    pragma_rules: ParseRules = [
        (template_ast.ImportNode, import_pragma),
        (template_ast.StyleNode, style_pragma),
        (template_ast.ComponentNode, component_prgama),
        (tags.IncludeTag, include_pragma),
        (tags.LayoutTag, layout_pragma),
        (tags.ParameterTag, parameter_pragma),
        (tags.SlotStartTag, slot_pragma),
        (tags.BlockStartTag, block_pragma),
    ]

    ctx = TemplateInfo(css)

    for tag in stream:
        for rule_tag, func in pragma_rules:
            if isinstance(tag, rule_tag):
                func(ctx, tag)

    return ctx


def include_pragma(
    ctx: TemplateInfo, tag: tags.IncludeTag
) -> t.Optional[template_ast.Node]:
    ctx.style_includes.add(tag.template)


def style_pragma(
    ctx: TemplateInfo, tag: tags.IncludeTag
) -> t.Optional[template_ast.Node]:
    if ctx.styles_set:
        raise ValueError("Template cannot have multiple styles tags")

    ctx.styles_set = True
    return template_ast.StyleNode()


def layout_pragma(
    ctx: TemplateInfo, tag: tags.LayoutTag
) -> t.Optional[template_ast.Node]:
    if ctx.layout is not None:
        raise ValueError("Template cannot have multiple layout tags")

    ctx.layout = tag.template
    return None


def parameter_pragma(
    ctx: TemplateInfo, tag: tags.ParameterTag
) -> t.Optional[template_ast.Node]:
    ctx.parameters.append(
        template_ast.TemplateParameter(
            name=tag.name,
            default=tag.default,
            type=tag.type,
        )
    )
    return None


def component_prgama(
    ctx: TemplateInfo, tag: template_ast.ComponentNode
) -> t.Optional[template_ast.Node]:
    call = template_ast.ComponentNode(
        component_name=tag.component_name, keywords=tag.keywords
    )
    ctx.components_calls.append(call)
    return call


def slot_pragma(ctx: TemplateInfo, token: tags.SlotStartTag) -> None:
    ctx.is_layout = True

    if token.name is None:
        if ctx.has_default_slot:
            raise ValueError("Template cannot have multiple default slots")

        ctx.has_default_slot = True

    slot = template_ast.SlotInfo(
        name=token.name,
        is_required=token.is_required,
    )
    ctx.slots.append(slot)


def block_pragma(ctx: TemplateInfo, token: tags.SlotStartTag) -> None:
    if token.name is not None:
        ctx.blocks.add(token.name)


def import_pragma(ctx: TemplateInfo, token: template_ast.ImportNode) -> None:
    ctx.imports.append(token)
