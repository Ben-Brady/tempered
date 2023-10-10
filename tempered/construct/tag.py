from ..template import TemplateTag, BlockIf, BlockFor, BlockExpr, BlockLiteral, BlockStyle
from .utils import value_to_constant, create_concat_chain, create_escape_call
import ast
import random
import rcssmin
from typing import Sequence, assert_never
import tinycss2
from tinycss2.ast import QualifiedRule


def construct_tag(tag: TemplateTag, result_value: ast.Name) -> Sequence[ast.AST]:
    match tag:
        case BlockLiteral():
            return construct_literal(tag, result_value)
        case BlockStyle():
            return construct_style(tag, result_value)
        case BlockExpr():
            return construct_expr(tag, result_value)
        case BlockIf():
            return construct_if(tag, result_value)
        case BlockFor():
            return construct_for(tag, result_value)
        case e:
            assert_never(e)


def construct_literal(
        tag: BlockLiteral,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    return [
        ast.AugAssign(
            target=result_value,
            op=ast.Add(),
            value=value_to_constant(tag.body)
        )
    ]


def construct_expr(
        tag: BlockExpr,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    return [
        ast.AugAssign(
            target=result_value,
            op=ast.Add(),
            value=create_escape_call(tag.value)
        )
    ]


def construct_if(
        block: BlockIf,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    if_block = []
    else_block = []

    for tag in block.if_block:
        if_block.extend(construct_tag(tag, result_value))

    if block.else_block:
        for tag in block.else_block:
            else_block.extend(construct_tag(tag, result_value))

    return [
        ast.If(
            test=block.condition,
            body=if_block,
            orelse=else_block,
        )
    ]


def construct_for(
        block: BlockFor,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    body = []
    for tag in block.loop_block:
        body.extend(construct_tag(tag, result_value))

    return [
        ast.For(
            target=block.loop_variable,
            iter=block.iterable,
            body=body,
            orelse=[],
        )
    ]


def construct_style(
        tag: BlockStyle,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    if tag.is_global:
        return create_global_style(tag, result_value)
    else:
        return create_scoped_style(tag, result_value)


def create_global_style(
        tag: BlockStyle,
        result_value: ast.Name
        ) -> Sequence[ast.AST]:
    css = str(tag.css)
    css = str(rcssmin.cssmin(css))
    if css == "":
        return []
    else:
        return [
            ast.AugAssign(
                target=result_value,
                op=ast.Add(),
                value=value_to_constant(css)
            ),
    ]


def create_scoped_style(
        tag: BlockStyle,
        result_value: ast.Name,
        ) -> Sequence[ast.AST]:
    css_tokens = tinycss2.parse_stylesheet(tag.css)
    unique_id = _generate_scoped_style_id()
    ID_RULE = tinycss2.parse_one_rule(f"#{unique_id} {{}}")
    ID_TOKEN, WHITESPACE_TOKEN = ID_RULE.prelude[:2]
    for token in css_tokens:
        if isinstance(token, QualifiedRule):
            token.prelude.insert(0, ID_TOKEN)
            token.prelude.insert(1, WHITESPACE_TOKEN)

    css = tinycss2.serialize(css_tokens)
    css = rcssmin.cssmin(css)

    if css == "":
        return []
    else:
        return [
            ast.AugAssign(
                target=result_value,
                op=ast.Add(),
                value=create_concat_chain(
                    value_to_constant(
                        f"<div style='display:contents;' id='{unique_id}'>"
                    ),
                    result_value,
                    value_to_constant("</div>"),
                )
            ),
            ast.AugAssign(
                target=result_value,
                op=ast.Add(),
                value=value_to_constant(f"<style>{css}</style>")
            ),
        ]


counter = 0
def _generate_scoped_style_id() -> str:
    global counter
    counter += 1
    return hex(counter)[2:]
