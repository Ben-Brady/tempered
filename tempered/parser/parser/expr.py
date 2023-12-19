from ... import ast_utils
from ..template_ast import TemplateParameter
import ast
import keyword


def parse_parameter(parameter: str) -> TemplateParameter:
    expr = parse_stmt(parameter)

    if isinstance(expr, ast.AnnAssign) and isinstance(expr.target, ast.Name):
        # name: type | name: type = default
        return TemplateParameter(
            name=expr.target.id,
            type=expr.annotation,
            default=expr.value,
        )
    elif (
        isinstance(expr, ast.Assign)
        and isinstance(expr.targets, list)
        and isinstance(expr.targets[0], ast.Name)
        ):
        # name = default
        return TemplateParameter(
            name=expr.targets[0].id,
            default=expr.value,
        )
    elif isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Name):
        # name
        return TemplateParameter(name=expr.value.id)
    else:
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

    return ast_utils.Name(expr)
