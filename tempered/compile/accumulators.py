from .. import ast_utils
import ast
from typing_extensions import Self


class ExprBuffer:
    _stack: list[ast.expr]

    def __init__(self):
        self._stack = []

    def add(self, value: ast.expr):
        self._stack.append(value)

    def empty(self) -> bool:
        return len(self._stack) == 0

    def flush(self) -> ast.expr | None:
        if len(self._stack) == 0:
            return None

        if len(self._stack) == 1:
            expr = self._stack[0]
        elif len(self._stack) < 100:
            expr = ast_utils.FormatString(*self._stack)
        else:
            expr = ast_utils.ArrayJoin(ast_utils.List(self._stack))

        self._stack.clear()
        return expr


class StringVariable:
    variable: ast.Name
    assigned: bool = False

    def __init__(self, name: str | ast.Name):
        if isinstance(name, str):
            name = ast_utils.Name(name)
        self.variable = name

    def create_add(self, value: ast.expr) -> ast.stmt:
        if self.assigned:
            return ast_utils.AddAssign(target=self.variable, value=value)
        else:
            self.assigned = True
            return ast_utils.Assign(target=self.variable, value=value)

    def ensure_assigned(self) -> list[ast.stmt]:
        if self.assigned:
            return []

        self.assigned = True
        return [ast_utils.Assign(target=self.variable, value=ast_utils.EmptyStr)]
