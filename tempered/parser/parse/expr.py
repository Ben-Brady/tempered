from ..parse_ast import *
from ..lexer import *
import ast
import keyword


def parse_parameter(parameter: str) -> TemplateParameter:
    module = ast.parse(parameter)
    if not isinstance(module, ast.Module):
        raise ValueError(f"Invalid Parameter: {parameter}")

    expr = module.body[0]
    match expr:
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=annotation,
            value=default
        ):
            return TemplateParameter(
                name=name,
                type=annotation,
                default=default if default is not None else RequiredParameter()
            )
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=annotation,
        ):
            return TemplateParameter(
                name=name,
                type=annotation,
            )
        case ast.Assign(
            targets=[ast.Name(id=name)],
            value=default
        ):
            return TemplateParameter(
                name=name,
                default=default
            )
        case ast.Expr(
            value=ast.Name(id=name)
        ):
            return TemplateParameter(name=name)
        case _:
            raise ValueError(f"Invalid Parameter: {parameter}")


def parse_expr(expression: str) -> ast.expr:
    expr = parse_stmt(expression)
    if isinstance(expr, ast.Expr):
        return expr.value
    elif isinstance(expr, ast.expr):
        return expr
    else:
        raise ValueError(f"Invalid Expr: {expression}")


def parse_stmt(expression: str) -> ast.stmt:
    module = ast.parse(expression)
    if not isinstance(module, ast.Module):
        raise ValueError(f"Invalid Expr: {expression}")

    stmt = module.body[0]
    return stmt


def parse_ident(expr: str) -> ast.Name:
    if keyword.iskeyword(expr):
        raise ValueError(f"Invalid identifier: {expr}")

    return ast.Name(id=expr)
