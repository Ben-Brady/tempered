from .utils import KWARGS_VARIABLE, WITH_STYLES_PARAMETER
import ast
import builtins
from functools import lru_cache
import typing_extensions as t


def convert_unknown_variables_to_kwargs(body: t.List[ast.stmt], known_names: t.List[str]):
    transformer = NameTransformer(known_names)
    for node in body:
        transformer.visit(node)


class NameTransformer(ast.NodeTransformer):
    RESERVED_NAMES = (
        KWARGS_VARIABLE,
        WITH_STYLES_PARAMETER,
    )

    def __init__(self, known_names: t.List[str]):
        self.known_names = known_names

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.known_names.append(target.id)

        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        return self.transform(node)

    def visit_For(self, node: ast.For):
        loop_vars = extract_loop_variables(node.target)
        self.known_names.extend(loop_vars)
        output_node = self.generic_visit(node)
        for _ in range(len(loop_vars)):
            self.known_names.pop()

        return output_node

    def visit_ListComp(self, node: ast.ListComp):
        return self._comprehension(node)

    def visit_SetComp(self, node: ast.SetComp):
        return self._comprehension(node)

    def visit_DictComp(self, node: ast.DictComp):
        return self._comprehension(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        return self._comprehension(node)

    def _comprehension(
        self, node: t.Union[ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp]
    ):
        loop_vars = []
        for generator in node.generators:
            loop_vars.extend(extract_loop_variables(generator.target))

        self.known_names.extend(loop_vars)

        if isinstance(node, ast.DictComp):
            node.key = self.visit(node.key)
            node.value = self.visit(node.value)
        else:
            node.elt = self.visit(node.elt)

        node.generators = [
            t.cast(ast.comprehension, self.generic_visit(generator))
            for generator in node.generators
        ]

        for _ in range(len(loop_vars)):
            self.known_names.pop()

        return node

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


def extract_loop_variables(target: ast.expr) -> t.List[str]:
    if isinstance(target, ast.Name):
        # `for a in x:`
        return [target.id]
    elif isinstance(target, ast.Tuple):
        # `for a, b in x:`
        return [elt.id for elt in target.elts if isinstance(elt, ast.Name)]
    else:
        # ¯\_(ツ)_/¯
        # TODO: Deal with case for loop is non standard
        return []


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
