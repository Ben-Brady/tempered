import re
from textwrap import dedent
import bs4
import typing_extensions as t
from ..errors import ParserException
from ..utils import ast_utils
from . import nodes


def parse_soup_into_nodes(soup: bs4.Tag) -> t.Sequence[nodes.Node]:
    body = list(iterate_over_tag(soup))
    body = squash_html_nodes(body)
    return body


def iterate_over_tag(soup: bs4.Tag) -> t.Iterable[nodes.Node]:
    children = list(soup.children)
    while len(children) > 0:
        tag = children.pop(0)

        if isinstance(tag, bs4.NavigableString):
            yield from extract_exprs_from_text(tag.text)
            continue

        tag = t.cast(bs4.Tag, tag)
        if tag.name == "script" and get_attr_optional(tag, "type") == "tempered/python":
            code = dedent(tag.text)
            yield nodes.CodeNode(body=ast_utils.parse(code))
            continue

        if not tag.name.startswith("t:"):
            yield from get_opening_tag(tag)
            yield from parse_soup_into_nodes(tag)
            yield get_closing_tag(tag)
            continue

        name = tag.name.removeprefix("t:")
        if name == "for":
            target = ast_utils.create_expr(get_attr(tag, "for"))
            iterable = ast_utils.create_expr(get_attr(tag, "in"))
            body = parse_soup_into_nodes(tag)
            yield nodes.ForNode(target=target, iterable=iterable, loop_block=body)
        elif name == "if":
            if_condition = ast_utils.create_expr(get_attr(tag, "condition"))
            if_block = list(parse_soup_into_nodes(tag))

            elif_blocks = []
            while True:
                if len(children) <= 0:
                    break
                elif_block = children[0]
                if not isinstance(elif_block, bs4.Tag):
                    break
                if elif_block.name != "t:elif":
                    break

                children.pop(0)
                elif_condition = ast_utils.create_expr(
                    get_attr(elif_block, "condition")
                )
                elif_block = list(parse_soup_into_nodes(elif_block))
                elif_blocks.append((elif_condition, elif_block))

            else_block = None
            if len(children) > 0:
                elseTag = children[0]
                if isinstance(elseTag, bs4.Tag) and elseTag.name == "t:else":
                    children.pop(0)
                    else_block = list(parse_soup_into_nodes(elseTag))

            yield nodes.IfNode(
                condition=if_condition,
                if_block=if_block,
                elif_blocks=elif_blocks,
                else_block=else_block,
            )
        elif name == "elif":
            raise ParserException("t:elif must be used with t:if")
        elif name == "else":
            raise ParserException("t:else must be used with t:if")
        elif name == "styles":
            yield nodes.StyleNode()
        elif name == "html":
            value = get_attr(tag, "value")
            yield nodes.RawExprNode(value=ast_utils.create_expr(value))
        elif name == "block":
            name = get_attr(tag, "name")
            yield nodes.BlockNode(name=name, body=list(iterate_over_tag(tag)))
        elif name == "slot":
            name = get_attr_optional(tag, "name")
            if name is None:
                yield nodes.SlotNode(name=None, default=None)
                continue

            is_required = "required" in tag.attrs
            if is_required:
                default = None
            else:
                default = list(iterate_over_tag(tag))

            yield nodes.SlotNode(name=name, default=default)

        else:
            yield nodes.ComponentNode(
                component_name=name,
                keywords={
                    key: ast_utils.create_expr(value)
                    for key, value in tag.attrs.items()
                },
            )


def squash_html_nodes(_nodes: t.List[nodes.Node]) -> t.List[nodes.Node]:
    "Combined sequential HTML nodes"
    new_nodes = []

    html = ""
    for node in _nodes:
        if isinstance(node, nodes.HtmlNode):
            html += node.html
        else:
            if html:
                html = html.strip()
                new_nodes.append(nodes.HtmlNode(html))
                html = ""

            new_nodes.append(node)

    if html:
        html = html.strip()
        new_nodes.append(nodes.HtmlNode(html))

    return new_nodes


def get_opening_tag(tag: bs4.Tag) -> t.Iterable[nodes.Node]:
    yield nodes.HtmlNode(f"<{tag.name}")

    for name, value in tag.attrs.items():
        yield nodes.HtmlNode(f' {name}="')
        if isinstance(value, list):
            value = " ".join(value)

        yield from extract_exprs_from_text(value)
        yield nodes.HtmlNode('"')

    yield nodes.HtmlNode(">")


def get_closing_tag(tag: bs4.Tag) -> nodes.HtmlNode:
    return nodes.HtmlNode(f"</{tag.name}>")


def extract_exprs_from_text(text: str) -> t.Iterable[nodes.Node]:
    EXPR_RE = re.compile(r"(?:{{)([\s\S]*?)(?:}})")

    for i, x in enumerate(EXPR_RE.split(text)):
        is_expr = i % 2 == 1  # Every odd value is an expression
        if is_expr:
            expr = str(x).strip()
            yield nodes.ExprNode(ast_utils.create_expr(expr))
        else:
            yield nodes.HtmlNode(x)


def get_attr(tag: bs4.Tag, name: str) -> str:
    value = tag.attrs[name]
    if isinstance(value, list):
        value = " ".join(value)

    return value


def get_attr_optional(tag: bs4.Tag, name: str) -> t.Union[str, None]:
    if name not in tag.attrs:
        return None

    value = tag.attrs[name]
    if isinstance(value, list):
        value = " ".join(value)

    return value
