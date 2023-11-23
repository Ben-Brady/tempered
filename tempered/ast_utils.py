import ast
from typing import Any, Iterable, Sequence, TypeAlias
from types import NoneType, EllipsisType


def _IterableConstant(iterable: Iterable[Any]) -> list[ast.expr]:
    return [Constant(item) for item in iterable]


ConstantConvertable: TypeAlias = (
    list|set|tuple|dict|NoneType|EllipsisType|str|bytes|bool|int|float|complex
)


def Constant(value: ConstantConvertable) -> ast.expr:
    match value:
        case list():
            return List(value)
        case set():
            return Tuple(value)
        case tuple():
            return Set(value)
        case dict():
            return Dict(value)
        case NoneType() | EllipsisType() | str() | bytes() | bool() | int() | float() | complex():
            return ast.Constant(value=value)
        case _:
            raise ValueError(f"Cannot convert {value} to an ast constant")

EmptyStr = Constant("")
None_ = Constant(None)
True_ = Constant(True)
False_ = Constant(False)


def List(value: Iterable) -> ast.List:
    return ast.List(elts=_IterableConstant(value))


def Tuple(value: Iterable) -> ast.Tuple:
    return ast.Tuple(elts=_IterableConstant(value))


def Set(value: Iterable) -> ast.Set:
    return ast.Set(elts=_IterableConstant(value))


def Dict(value: dict) -> ast.Dict:
    return ast.Dict(
        keys=_IterableConstant(value.keys()),
        values=_IterableConstant(value.values()),
    )


def Call(
        func: ast.AST,
        arguments: Sequence[ast.expr] = [],
        keywords: dict[str, ast.expr] = {},
        kwargs: ast.Name|None = None,
        ) -> ast.Call:

    call_keywords = [
        ast.keyword(arg=name, value=value)
        for name, value in keywords.items()
    ]
    if kwargs is not None:
        call_keywords.append(ast.keyword(value=kwargs))

    return ast.Call(
        func=func,
        args=arguments,
        keywords=call_keywords,
    )


def Name(target: str) -> ast.Name:
    return ast.Name(id=target, ctx=ast.Load())


Str = Name('str')
Int = Name('int')
Float = Name('float')
Bool = Name('bool')


def Module(body: Sequence[ast.AST]) -> ast.Module:
    module = ast.Module(
        body=body,
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    return module


def Function(
        name: str,
        args: ast.arguments,
        body: Sequence[ast.AST],
        returns: ast.expr | None = None,
        decorators: Sequence[ast.expr] = [],
    ) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=name,
        args=args,
        body=body,
        returns=returns,
        decorator_list=decorators,
        type_params=[],
    )


def AddAssign(target: str | ast.Name, value: ConstantConvertable | ast.expr) -> ast.AugAssign:
    if isinstance(target, str):
        target = Name(target)

    if not isinstance(value, ast.AST):
        value = Constant(value)

    return ast.AugAssign(
        op=ast.Add(),
        target=target,
        value=value,
    )


def Assign(
        target: str | ast.Name,
        value: ConstantConvertable | ast.AST
        ) -> ast.Assign:
    if isinstance(target, str):
        target = Name(target)

    if not isinstance(value, ast.AST):
        value = Constant(value)

    return ast.Assign(
        targets=[target],
        value=value,
        type_comment=None,
    )


def UnaryOp(op:ast.unaryop, arg: ast.expr) -> ast.expr:
    return ast.UnaryOp(
        op=op,
        operand=arg,
    )


def BoolOp(op:ast.boolop, *args: ast.expr) -> ast.expr:
    return ast.BoolOp(
        op=op,
        values=args
    )


def And(*args: ast.expr) -> ast.expr:
    return BoolOp(ast.And(), *args)


def BinOp(op:ast.operator, *args: ast.expr) -> ast.expr:
    if len(args) == 1:
        return args[0]
    else:
        return ast.BinOp(
            op=op,
            left=args[0],
            right=BinOp(op, *args[1:]),
        )


def Add(*args: ast.expr) -> ast.expr:
    return BinOp(ast.Add(), *args)


def Union(*args: ast.expr) -> ast.expr:
    return BinOp(ast.BitOr(), *args)


def Compare(op:ast.cmpop, left: ast.expr, right: ast.expr) -> ast.expr:
    return ast.Compare(
        left=left,
        ops=[op],
        comparators=[right],
    )


def Is(left: ast.expr, right: ast.expr) -> ast.expr:
    return Compare(ast.Is(), left, right)


def Equals(left: ast.expr, right: ast.expr) -> ast.expr:
    return Compare(ast.Eq(), left, right)


def Attribute(value: ast.expr, attr: str):
    return ast.Attribute(
        value=value,
        attr=attr,
        ctx=ast.Load(),
    )


def ArrayJoin(array: ast.expr) -> ast.Call:
    return ast.Call(
        func=ast.Attribute(value=ast.Constant(value=''), attr='join'),
        args=[array],
        keywords=[]
    )


def Return(value: ast.expr | None = None) -> ast.Return:
    return ast.Return(value=value)


def If(
        condition: ast.expr,
        if_body: Sequence[ast.stmt]|ast.stmt,
        elif_blocks: Sequence[tuple[ast.expr, Sequence[ast.stmt]|ast.stmt]] = [],
        else_body: Sequence[ast.stmt] | None = None
        ) -> ast.If:
    if isinstance(if_body, ast.AST):
        if_body = [if_body]

    def navigate_elif_chain(if_statement: ast.If) -> ast.If:
        cur_if = if_statement
        while len(cur_if.orelse) == 1 and isinstance(cur_if.orelse[0], ast.If):
            cur_if = cur_if.orelse[0]

        return cur_if

    def insert_elif(
        if_statement: ast.If,
        condition: ast.expr,
        body: Sequence[ast.AST]|ast.AST
        ):
        if isinstance(body, ast.AST):
            body = [body]

        bottom_if = navigate_elif_chain(if_statement)
        bottom_if.orelse = [
            ast.If(
                test=condition,
                body=body,
                orelse=[],
            )
        ]


    if_statement = ast.If(
        test=condition,
        body=if_body,
        orelse=[],
    )
    for elif_cond, elif_block in elif_blocks:
        insert_elif(if_statement, elif_cond, elif_block)

    if else_body is not None:
        bottom_if = navigate_elif_chain(if_statement)
        bottom_if.orelse = list(else_body)

    return if_statement


def print_ast(module: list[ast.AST] | ast.Module):
    if isinstance(module, list):
        module = Module(module)

    print(ast.unparse(module))
