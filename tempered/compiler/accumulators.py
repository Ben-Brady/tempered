from .. import ast_utils
import ast
import typing_extensions as t


class ExprBuffer:
    _stack: t.List[ast.expr]

    def __init__(self):
        self._stack = []

    def add(self, value: ast.expr):
        self._stack.append(value)

    def empty(self) -> bool:
        return len(self._stack) == 0

    def flush(self) -> t.Union[ast.expr, None]:
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
    name: ast.Name
    assigned: bool = False

    def __init__(self, name: t.Union[str, ast.Name]):
        if isinstance(name, str):
            name = ast_utils.Name(name)
        self.name = name

    def create_add(self, value: ast.expr) -> ast.stmt:
        if self.assigned:
            return ast_utils.AddAssign(target=self.name, value=value)
        else:
            self.assigned = True
            return ast_utils.Assign(target=self.name, value=value)

    def ensure_assigned(self) -> t.List[ast.stmt]:
        if self.assigned:
            return []

        self.assigned = True
        return [ast_utils.Assign(target=self.name, value=ast_utils.EmptyStr)]
