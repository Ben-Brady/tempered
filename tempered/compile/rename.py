from .utils import KWARGS_VARIABLE
import ast
from typing import cast
from functools import lru_cache


def convert_unknown_variables_to_kwargs(body: list[ast.stmt], known_names: list[str]):
    transformer = NameTransformer(known_names)
    for node in body:
        transformer.visit(node)


class NameTransformer(ast.NodeTransformer):
    def __init__(self, known_names: list[str]):
        self.known_names = known_names

    def visit_For(self, node: ast.For):
        if not isinstance(node.target, ast.Name):
            return self.generic_visit(node)

        self.known_names.append(node.target.id)
        node = cast(ast.For, self.generic_visit(node))
        self.known_names.pop()
        return node

    def visit_Name(self, node: ast.Name):
        return self.transform(node)

    def transform(self, node: ast.Name) -> ast.expr:
        if any(
            (
                node.id == KWARGS_VARIABLE,
                node.id.startswith("__"),
                node.id in self.known_names,
                is_builtin(node.id),
            )
        ):
            return node

        return ast.Subscript(
            value=ast.Name(KWARGS_VARIABLE, ctx=ast.Load()),
            slice=ast.Constant(value=node.id),
            ctx=getattr(node, "ctx", ast.Load()),
        )


@lru_cache(maxsize=512)
def is_builtin(name: str):
    if name in dir(__builtins__):
        return True

    try:
        eval(name, {}, {})
    except NameError:
        return False
    else:
        return True
