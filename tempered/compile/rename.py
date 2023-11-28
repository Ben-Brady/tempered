from .utils import KWARGS_VARIABLE, WITH_STYLES_PARAMETER
import ast
from typing import cast
from functools import lru_cache
import builtins


def convert_unknown_variables_to_kwargs(body: list[ast.stmt], known_names: list[str]):
    transformer = NameTransformer(known_names)
    for node in body:
        transformer.visit(node)


class NameTransformer(ast.NodeTransformer):
    RESERVED_NAMES = (
        KWARGS_VARIABLE,
        WITH_STYLES_PARAMETER,
    )

    def __init__(self, known_names: list[str]):
        self.known_names = known_names

    def visit_For(self, node: ast.For):
        if isinstance(node.target, ast.Name):
            loop_vars = [node.target.id]
        elif isinstance(node.target, ast.Tuple):
            loop_vars = [
                elt.id for elt in node.target.elts if isinstance(elt, ast.Name)
            ]
        else:
            # TODO: Deal with case for loop is non standard
            # e.g. not `for x in y:` or `for a, b in y:`
            loop_vars = []

        self.known_names.extend(loop_vars)
        output_node = self.generic_visit(node)
        for _ in range(len(loop_vars)):
            self.known_names.pop()
        return output_node

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.known_names.append(target.id)

        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        return self.transform(node)

    def transform(self, node: ast.Name) -> ast.expr:
        if (
            node.id.startswith("__")
            or node.id in self.RESERVED_NAMES
            or node.id in self.known_names
            or is_builtin(node.id)
        ):
            return node

        return ast.Subscript(
            value=ast.Name(KWARGS_VARIABLE, ctx=ast.Load()),
            slice=ast.Constant(value=node.id),
            ctx=getattr(node, "ctx", ast.Load()),
        )


@lru_cache(maxsize=2048)
def is_builtin(name: str):
    if name in dir(builtins):
        return True

    try:
        eval(name, {}, {})
    except NameError:
        return False
    else:
        return True
