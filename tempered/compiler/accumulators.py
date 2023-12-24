from .. import ast_utils
import ast
import typing_extensions as t


class Variable:
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
