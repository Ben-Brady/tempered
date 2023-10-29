import ast
from typing import Any, Iterable, Sequence
from types import NoneType, EllipsisType


def _create_iterable_constant(iterable: Iterable[Any]) -> list[ast.expr]:
    return [create_constant(item) for item in iterable]


def create_constant(value: Any) -> ast.expr:
    match value:
        case list():
            return create_list(value)
        case set():
            return create_tuple(value)
        case tuple():
            return create_set(value)
        case dict():
            return create_dict(value)
        case NoneType() | EllipsisType() | str() | bytes() | bool() | int() | float() | complex():
            return ast.Constant(value=value)
        case type():
            raise ValueError(f"Cannot convert {value} to an ast constant")
        case _:
            raise ValueError(f"Cannot convert {value} to an ast constant")

def create_list(value: Iterable) -> ast.List:
    return ast.List(elts=_create_iterable_constant(value))

def create_tuple(value: Iterable) -> ast.Tuple:
    return ast.Tuple(elts=_create_iterable_constant(value))

def create_set(value: Iterable) -> ast.Set:
    return ast.Set(elts=_create_iterable_constant(value))

def create_dict(value: dict) -> ast.Dict:
    return ast.Dict(
        keys=_create_iterable_constant(value.keys()),
        values=_create_iterable_constant(value.values()),
    )

def create_call(
        func: ast.AST,
        args: Sequence[ast.expr] = [],
        keywords: dict[str, ast.expr] = {},
        ) -> ast.Call:
    return ast.Call(
        func=func,
        args=args,
        keywords=[
            ast.keyword(arg=name, value=value)
            for name, value in keywords.items()
        ],
    )


def create_name(target: str) -> ast.Name:
    return ast.Name(id=target)


def create_module(body: Sequence[ast.AST]) -> ast.Module:
    module = ast.Module(
        body=body,
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    return module


def create_function(
        name: str,
        args: ast.arguments,
        body: Sequence[ast.AST],
        returns: ast.expr | None = None
    ) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=name,
        args=args,
        body=body,
        returns=returns,
        decorator_list=[],
        type_params=[],
    )


def create_if(
        condition: ast.AST,
        if_body: Sequence[ast.AST]|ast.AST,
        else_body: Sequence[ast.AST] | None = None
        ) -> ast.If:
    if not isinstance(if_body, Sequence):
        if_body = [if_body]

    else_body = else_body or []
    return ast.If(test=condition, body=if_body, orelse=else_body)


def create_add_assign(target: str|ast.Name, value: Any|ast.expr) -> ast.AugAssign:
    if isinstance(target, str):
        target = create_name(target)

    if not isinstance(value, ast.AST):
        value = create_constant(value)

    return ast.AugAssign(
        op=ast.Add(),
        target=target,
        value=value,
    )


def create_assignment(target: str|ast.Name, value: Any) -> ast.Assign:
    if isinstance(target, str):
        target = create_name(target)

    return ast.Assign(
        targets=[target],
        value=create_constant(value),
        type_comment=None,
    )


def create_string_concat(*args: ast.expr) -> ast.expr:
    if len(args) == 1:
        return args[0]
    else:
        return ast.BinOp(
            left=args[0],
            op=ast.Add(),
            right=create_string_concat(*args[1:]),
        )


def create_attribute(value: ast.expr, attr: str):
    return ast.Attribute(
        value=value,
        attr=attr,
    )


def create_array_join(array: ast.expr) -> ast.Call:
    return ast.Call(
        func=ast.Attribute(value=ast.Constant(value=''), attr='join'),
        args=[array],
        keywords=[]
    )

def create_return(value: ast.expr | None = None) -> ast.Return:
    return ast.Return(value=value)
