import ast
from typing_extensions import Any, Iterable, Sequence
import typing_extensions as t
import sys


NoneType = type(None)
EllipsisType = type(...)

LiteralType: t.TypeAlias = t.Union[
    list,
    set,
    tuple,
    dict,
    NoneType,
    EllipsisType,
    str,
    bytes,
    bool,
    int,
    float,
    complex,
]


def Constant(value: LiteralType) -> ast.expr:
    if isinstance(value, list):
        return List(value)
    elif isinstance(value, set):
        return Tuple(value)
    elif isinstance(value, tuple):
        return Set(value)
    elif isinstance(value, dict):
        return Dict(value)
    elif isinstance(value, (NoneType, EllipsisType, str, bytes, bool, int, float, complex)):
        return ast.Constant(value=value)
    else:
        raise ValueError(f"Cannot convert {value} to an ast constant")


EmptyStr = Constant("")
None_ = Constant(None)
True_ = Constant(True)
False_ = Constant(False)


def List(value: Iterable[t.Union[LiteralType, ast.expr]]) -> ast.List:
    return ast.List(elts=_IterableConstant(value))


def Tuple(value: Iterable[t.Union[LiteralType, ast.expr]]) -> ast.Tuple:
    return ast.Tuple(elts=_IterableConstant(value))


def Set(value: Iterable[t.Union[LiteralType, ast.expr]]) -> ast.Set:
    return ast.Set(elts=_IterableConstant(value))


def Dict(value: dict) -> ast.Dict:
    return ast.Dict(
        keys=_IterableConstant(value.keys()),
        values=_IterableConstant(value.values()),
    )


def _IterableConstant(iterable: Iterable[t.Union[LiteralType, ast.expr]]) -> t.List[ast.expr]:
    values = []
    for item in iterable:
        if not isinstance(item, ast.AST):
            item = Constant(item)
        values.append(item)

    return values


def Call(
    func: ast.AST,
    arguments: Sequence[ast.expr] = [],
    keywords: t.Dict[str, ast.expr] = {},
    kwargs: t.Union[ast.Name, None] = None,
) -> ast.Call:
    call_keywords = [
        ast.keyword(arg=name, value=value) for name, value in keywords.items()
    ]
    if kwargs is not None:
        call_keywords.append(ast.keyword(value=kwargs))

    return ast.Call(
        func=func,
        args=arguments,
        keywords=call_keywords,
    )


def Name(ident: str) -> ast.Name:
    return ast.Name(id=ident, ctx=ast.Load())


Str = Name("str")
Int = Name("int")
Float = Name("float")
Bool = Name("bool")


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
    returns: t.Union[ast.expr, None] = None,
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


def AddAssign(target: t.Union[str, ast.Name], value: t.Union[LiteralType, ast.expr]) -> ast.AugAssign:
    if isinstance(target, str):
        target = Name(target)

    if not isinstance(value, ast.AST):
        value = Constant(value)

    return ast.AugAssign(
        op=ast.Add(),
        target=target,
        value=value,
    )


def Assign(target: t.Union[str, ast.expr], value: t.Union[LiteralType, ast.AST]) -> ast.Assign:
    if isinstance(target, str):
        target = Name(target)

    if not isinstance(value, ast.AST):
        value = Constant(value)

    return ast.Assign(
        targets=[target],
        value=value,
        type_comment=None,
    )


def UnaryOp(op: ast.unaryop, arg: ast.expr) -> ast.expr:
    return ast.UnaryOp(
        op=op,
        operand=arg,
    )


def BoolOp(op: ast.boolop, *args: ast.expr) -> ast.expr:
    return ast.BoolOp(op=op, values=args)


def And(*args: ast.expr) -> ast.expr:
    return BoolOp(ast.And(), *args)


def BinOp(op: ast.operator, *args: ast.expr) -> ast.expr:
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


def Compare(op: ast.cmpop, left: ast.expr, right: ast.expr) -> ast.expr:
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
        func=ast.Attribute(value=ast.Constant(value=""), attr="join"),
        args=[array],
        keywords=[],
    )


def Comprehension(
    loop_var: t.Union[str, ast.Name],
    iterable: ast.expr,
) -> ast.comprehension:
    if isinstance(loop_var, str):
        loop_var = Name(loop_var)

    return ast.comprehension(
        target=loop_var,
        iter=iterable,
        ifs=[],
        is_async=0,
    )


def GeneratorExp(
    expr: ast.expr,
    loop_var: t.Union[str, ast.Name],
    iterable: ast.expr,
) -> ast.GeneratorExp:
    return ast.GeneratorExp(
        elt=expr,
        generators=[Comprehension(loop_var, iterable)],
    )


def ListComp(
    expr: ast.expr,
    loop_var: t.Union[str, ast.Name],
    iterable: ast.expr,
) -> ast.ListComp:
    return ast.ListComp(
        elt=expr,
        generators=[Comprehension(loop_var, iterable)],
    )


def Return(value: t.Union[ast.expr, None] = None) -> ast.Return:
    return ast.Return(value=value)


def FormatString(*expressions: ast.expr) -> ast.expr:
    values = []
    for expr in expressions:
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            values.append(expr)
        else:
            values.append(ast.FormattedValue(value=expr, conversion=-1))

    return ast.JoinedStr(values=values)


IfBody: t.TypeAlias = t.Union[t.Sequence[ast.stmt], ast.stmt]
def If(
    condition: ast.expr,
    if_body: IfBody,
    elif_blocks: Sequence[t.Tuple[ast.expr, IfBody]] = [],
    else_body: t.Union[IfBody, None] = None,
) -> ast.If:
    if isinstance(if_body, ast.AST):
        if_body = [if_body]

    def navigate_elif_chain(if_statement: ast.If) -> ast.If:
        cur_if = if_statement
        while len(cur_if.orelse) == 1 and isinstance(cur_if.orelse[0], ast.If):
            cur_if = cur_if.orelse[0]

        return cur_if

    def insert_elif(if_statement: ast.If, condition: ast.expr, body: IfBody):
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
        if isinstance(else_body, ast.stmt):
            else_body = [else_body]

        bottom_if.orelse = list(else_body)

    return if_statement


def print_ast(module: t.Union[t.List[ast.AST], ast.Module]):
    if isinstance(module, list):
        module = Module(module)

    print(unparse(module))

def unparse(node: ast.AST):
    if sys.version_info >= (3, 9):
        return ast.unparse(node)
    else:
        import astor
        return astor.to_source(node)
