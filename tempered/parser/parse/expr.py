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
        case ast.Expr(
            value=ast.Name(id=name)
        ):
            return TemplateParameter(name=name)
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=ast.Name(id=type)|ast.Constant(value=type),
            value=ast.Name(id=default)|ast.Constant(value=default)
        ):
            return TemplateParameter(
                name=name,
                type=type if isinstance(type, str) else type.id,
                default=default if default is not None else RequiredParameter()
            )
        case ast.Assign(
            targets=[ast.Name(id=name)],
            value=ast.Constant(value=default)
        ):
            return TemplateParameter(
                name=name,
                default=default
            )
        case ast.AnnAssign(
            target=ast.Name(id=name),
            annotation=ast.Name(id=type)|ast.Constant(value=type),
        ):
            return TemplateParameter(
                name=name,
                type=type if isinstance(type, str) else type.id,
            )
        case _:
            raise ValueError(f"Invalid Parameter: {parameter}")


def parse_expr(expression: str) -> ast.expr:
    module = ast.parse(expression)
    if not isinstance(module, ast.Module):
        raise ValueError(f"Invalid Expr: {expression}")

    expr = module.body[0]
    if isinstance(expr, ast.Expr):
        return expr.value
    elif isinstance(expr, ast.expr):
        return expr
    else:
        raise ValueError(f"Invalid Expr: {expression}")




def parse_ident(expr: str) -> ast.Name:
    if keyword.iskeyword(expr):
        raise ValueError(f"Invalid identifier: {expr}")

    return ast.Name(id=expr)
