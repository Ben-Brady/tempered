from .. import ast_utils
import ast
from typing import Protocol


class Result(Protocol):
    def create_init(self) -> list[ast.stmt]:
        ...

    def create_add(self, value: ast.expr) -> ast.stmt:
        ...

    def create_value(self) -> ast.expr:
        ...


class StringResult(Result):
    _variable: ast.Name

    def __init__(self, name: str|ast.Name):
        if isinstance(name, str):
            name = ast_utils.Name(name)

        self._variable = name

    def create_init(self) -> list[ast.stmt]:
        return [ast_utils.Assign(
            target=self._variable,
            value="",
        )]

    def create_add(self, value: ast.expr) -> ast.stmt:
        return ast_utils.AddAssign(
            target=self._variable,
            value=value,
        )

    def create_value(self) -> ast.expr:
        return self._variable


class ArrayResult(Result):
    _variable: ast.Name

    def __init__(self, name: str):
        self._variable = ast_utils.Name(name)

    def create_init(self) -> list[ast.stmt]:
        return [ast_utils.Assign(
            target=self._variable,
            value=[],
        )]

    def create_add(self, value: ast.expr) -> ast.stmt:
        return ast.Expr(value=ast_utils.Call(
            func=ast_utils.Attribute(self._variable, 'append'),
            arguments=[value],
        ))

    def create_value(self) -> ast.expr:
        return ast_utils.ArrayJoin(self._variable)

