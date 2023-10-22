import ast
from typing import Any, Iterable, Sequence
from types import NoneType, EllipsisType
from .compile.constants import ESCAPE_FUNC_NAME
from .parser import RequiredParameter, TemplateParameter


def create_constant(value: Any) -> ast.expr:
    def create_iterable_constant(iterable: Iterable[Any]) -> list[ast.expr]:
        return [
            create_constant(item)
            for item in iterable
        ]

    match value:
        case list():
            return ast.List(
                elts=create_iterable_constant(value)
            )
        case set():
            return ast.Set(
                elts=create_iterable_constant(value)
            )
        case tuple():
            return ast.Tuple(
                elts=create_iterable_constant(value)
            )
        case dict():
            return ast.Dict(
                keys=create_iterable_constant(value.keys()),
                values=create_iterable_constant(value.values()),
            )
        case NoneType() | EllipsisType() | str() | bytes() | bool() | int() | float() | complex():
            return ast.Constant(value=value)
        case type():
            raise ValueError(f"Cannot convert {value} to an ast constant")
        case _:
            raise ValueError(f"Cannot convert {value} to an ast constant")



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


def create_escape_call(value: ast.expr) -> ast.expr:
    return create_call(ESCAPE_FUNC_NAME, [value])


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

def create_assignment(target: str|ast.Name, value: Any) -> ast.Assign:
    if isinstance(target, str):
        target = create_name(target)

    return ast.Assign(
        targets=[target],
        value=create_constant(value),
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


def create_arguments(
        arguments: list[TemplateParameter],
        kw_arguments: list[TemplateParameter]
        ) -> ast.arguments:
    def construct_default(param: TemplateParameter):
        match param.default:
            case RequiredParameter():
                return None
            case default:
                return create_constant(default)

    def create_annotation(annotation: str|None) -> ast.expr|None:
        if annotation:
            return create_constant(annotation)
        else:
            return None

    def create_argument_list(
            parameters: list[TemplateParameter]
            ) -> tuple[
                list[ast.arg],
                list[ast.expr|None]
            ]:
        args = [
            ast.arg(
                arg=param.name,
                annotation=create_annotation(param.type),
            )
            for param in parameters
        ]
        defaults = [
            construct_default(param)
            for param in parameters
        ]
        return args, defaults


    args, defaults = create_argument_list(arguments)
    kw_args, kw_defaults = create_argument_list(kw_arguments)


    return ast.arguments(
        args=args,
        defaults=defaults,
        kwonlyargs=kw_args,
        kw_defaults=kw_defaults,
        posonlyargs=[],
    )


def create_add_assign(target: str|ast.Name, value: str|ast.AST) -> ast.AugAssign:
    if isinstance(target, str):
        target = create_name(target)

    if not isinstance(value, ast.AST):
        value = create_constant(value)

    return ast.AugAssign(
        op=ast.Add(),
        target=target,
        value=value,
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
