import ast
import typing_extensions as t
from . import tags, template_ast
from .scanner import Scanner

TagScanner = Scanner[tags.Tag]
T = t.TypeVar("T", bound=tags.Tag)
ParseRules: t.TypeAlias = t.List[
    t.Tuple[
        t.Type[T],
        t.Callable[
            [TagScanner, T],
            t.Optional[template_ast.Node],
        ],
    ]
]


def parse_tags_to_template_ast(
    tags: t.Sequence[tags.Tag],
) -> template_ast.TemplateBlock:
    scanner = Scanner(tags)
    body = take_tags_until(scanner)
    return body


def next_tag(scanner: TagScanner) -> t.Optional[template_ast.Node]:
    tag = scanner.pop()
    parse_rules: ParseRules = [
        (tags.IfStartTag, take_if),
        (tags.ForStartTag, take_for),
        (tags.SlotStartTag, take_slot),
        (tags.BlockStartTag, take_block),
    ]

    for rule_tag, func in parse_rules:
        if isinstance(tag, tags.PragmaTag):
            return None
        if isinstance(tag, template_ast.SingleTagNode):
            return tag
        if isinstance(tag, rule_tag):
            return func(scanner, tag)

    if isinstance(tag, tags.SlotEndTag):
        raise ValueError("Slot not opened")
    elif isinstance(tag, tags.BlockEndTag):
        raise ValueError("Block not opened")
    elif isinstance(tag, (tags.ElIfTag, tags.ElseTag, tags.IfEndTag)):
        raise ValueError("If statement not openned")
    elif isinstance(tag, tags.ForEndTag):
        raise ValueError("For loop not opened")
    else:
        raise ValueError("Unknown Tag")


def take_tags_until(
    scanner: TagScanner,
    stop_tags: t.List[t.Type[tags.CompositeTag]] = [],
) -> t.List[template_ast.Node]:
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(scanner)
        if tag:
            tags.append(tag)

    return tags


def take_if(scanner: TagScanner, tag: tags.IfStartTag) -> template_ast.Node:
    if_block: t.List[template_ast.Node] = take_tags_until(
        scanner, stop_tags=[tags.ElIfTag, tags.ElseTag, tags.IfEndTag]
    )

    elif_blocks: t.List[t.Tuple[ast.expr, template_ast.TemplateBlock]] = []
    while scanner.is_next(tags.ElIfTag):
        elif_token = scanner.expect(tags.ElIfTag)
        block = take_tags_until(
            scanner, stop_tags=[tags.ElIfTag, tags.ElseTag, tags.IfEndTag]
        )
        elif_blocks.append((elif_token.condition, block))

    if scanner.accept(tags.ElseTag):
        else_block = take_tags_until(scanner, stop_tags=[tags.IfEndTag])
    else:
        else_block = None

    scanner.expect(tags.IfEndTag)
    return template_ast.IfNode(
        condition=tag.condition,
        if_block=if_block,
        elif_blocks=elif_blocks,
        else_block=else_block,
    )


def take_for(
    scanner: TagScanner, tag: tags.ForStartTag
) -> t.Union[template_ast.Node, None]:
    block = take_tags_until(scanner, stop_tags=[tags.ForEndTag])
    scanner.expect(tags.ForEndTag)

    return template_ast.ForNode(
        target=tag.target,
        iterable=tag.iterable,
        loop_block=block,
    )


def take_slot(
    scanner: TagScanner, tag: tags.SlotStartTag
) -> t.Union[template_ast.Node, None]:
    if tag.name is None:
        return template_ast.SlotNode(name=None, default=None)

    if tag.is_required:
        default_body = None
    else:
        default_body = take_tags_until(scanner=scanner, stop_tags=[tags.SlotEndTag])

        scanner.expect(tags.SlotEndTag)

    slot = template_ast.SlotNode(
        name=tag.name,
        default=default_body,
    )
    return slot


def take_block(
    scanner: TagScanner, tag: tags.BlockStartTag
) -> t.Union[template_ast.Node, None]:
    body = take_tags_until(scanner, stop_tags=[tags.BlockEndTag])
    scanner.expect(tags.BlockEndTag)

    return template_ast.BlockNode(
        name=tag.name,
        body=body,
    )
