from .. import ast_utils
import ast
from typing import Protocol

class Result(Protocol):
    def create_assignment(self) -> list[ast.AST]:
        ...

    def create_add(self, value: ast.expr) -> ast.AST:
        ...

    def create_build(self) -> ast.expr:
        ...


class StringResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.create_name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.create_assignment(
            target=self._variable,
            value="",
        )]

    def create_add(self, value: ast.expr) -> ast.AST:
        return ast_utils.create_add_assign(
            target=self._variable,
            value=value,
        )

    def create_build(self) -> ast.expr:
        return self._variable


class ArrayResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.create_name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.create_assignment(
            target=self._variable,
            value=[],
        )]

    def create_add(self, value: ast.expr) -> ast.AST:
        return ast.Expr(value=ast_utils.create_call(
            func=ast_utils.create_attribute(self._variable, 'append'),
            args=[value],
        ))

    def create_build(self) -> ast.expr:
        return ast_utils.create_array_join(self._variable)

