import ast
from .utils import KWARGS_VARIABLE


def convert_unknown_variables_to_kwargs(body: list[ast.stmt], known_names: list[str]):
    class NameTransformer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name):
            return transform(node)

    def transform(node: ast.Name) -> ast.expr:
        if any(
            (
                node.id == KWARGS_VARIABLE,
                node.id.startswith("__"),
                node.id in known_names,
                is_builtin(node.id),
            )
        ):
            return node

        return ast.Subscript(
            value=ast.Name(KWARGS_VARIABLE, ctx=ast.Load()),
            slice=ast.Constant(value=node.id),
            ctx=getattr(node, "ctx", ast.Load()),
        )

    transformer = NameTransformer()
    for node in body:
        transformer.visit(node)


def is_builtin(name: str):
    if name in dir(__builtins__):
        return True

    try:
        eval(name, {}, {})
    except NameError:
        return False
    else:
        return True
