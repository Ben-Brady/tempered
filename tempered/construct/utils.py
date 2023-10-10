import ast
from typing import Any, Iterable
from types import NoneType, EllipsisType
from .constants import ESCAPE_FUNC_NAME


def iterable_to_constant(iterable: Iterable[Any]) -> list[ast.expr]:
    return [
        value_to_constant(item)
        for item in iterable
    ]


def value_to_constant(value: Any) -> ast.expr:
    match value:
        case list():
            return ast.List(
                elts=iterable_to_constant(value)
            )
        case set():
            return ast.Set(
                elts=iterable_to_constant(value)
            )
        case tuple():
            return ast.Tuple(
                elts=iterable_to_constant(value)
            )
        case dict():
            return ast.Dict(
                keys=iterable_to_constant(value.keys()),
                values=iterable_to_constant(value.values()),
            )
        case NoneType() | EllipsisType() | str() | bytes() | bool() | int() | float() | complex():
            return ast.Constant(value=value)
        case _:
            raise ValueError(f"Cannot convert {value} to an ast constant")


def create_concat_chain(*args: ast.expr) -> ast.expr:
    if len(args) == 1:
        return args[0]
    else:
        return ast.BinOp(
            left=args[0],
            op=ast.Add(),
            right=create_concat_chain(*args[1:]),
        )


def create_escape_call(value: ast.expr) -> ast.expr:
    return ast.Call(
        func=ESCAPE_FUNC_NAME,
        args=[value],
        keywords=[],
    )
