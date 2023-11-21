from .. import ast_utils
import ast
from typing import Protocol


class Result(Protocol):
    def create_assignment(self) -> list[ast.AST]:
        ...

    def create_add(self, value: ast.expr) -> ast.stmt:
        ...

    def create_build(self) -> ast.expr:
        ...


class StringResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.Name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.Assignment(
            target=self._variable,
            value="",
        )]

    def create_add(self, value: ast.expr) -> ast.stmt:
        return ast_utils.AddAssign(
            target=self._variable,
            value=value,
        )

    def create_build(self) -> ast.expr:
        return self._variable


class ArrayResult(Result):
    _variable: ast.Name

    def __init__(self):
        self._variable = ast_utils.Name('__output')

    def create_assignment(self) -> list[ast.AST]:
        return [ast_utils.Assignment(
            target=self._variable,
            value=[],
        )]

    def create_add(self, value: ast.expr) -> ast.stmt:
        return ast.Expr(value=ast_utils.Call(
            func=ast_utils.Attribute(self._variable, 'append'),
            args=[value],
        ))

    def create_build(self) -> ast.expr:
        return ast_utils.ArrayJoin(self._variable)

