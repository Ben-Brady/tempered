from ..template import (
    RequiredParameter, TemplateParameter,
    Template, BlockLiteral
)
import ast
import re
import bs4
from typing import LiteralString, Any, cast
import minify_html


def parse_parameters(soup: bs4.BeautifulSoup) -> list[TemplateParameter]:
    Ws = r"\s*"
    Ident = r"[a-z_][a-z_0-9]*"
    Value = r"[0-9a-z_\[\]\(\)\"\']*"
    parameter_regex = re.compile("".join((
        "{", Ws,
        "param", Ws,
        Ident, Ws,
        f"(:{Ws}({Ident}|{Value}))?", Ws,
        f"(={Ws}({Ident}|{Value}))?", Ws,
        "}"
    )))

    parameters = []
    matches = parameter_regex.finditer(soup.text)
    for m in matches:
        declaration = m.group()
        declaration = declaration \
            .removeprefix("{") \
            .strip() \
            .removeprefix("declare") \
            .removesuffix("}") \
            .strip()

        body = ast.parse(declaration)
        if not isinstance(body, ast.Module):
            continue

        match body:
            case ast.Expr(
                value=ast.Name(id=name)
            ):
                parameters.append(TemplateParameter(name=name))
            case ast.Assign(
                targets=[ast.Name(id=name)],
                value=ast.Constant(value=default)
            ):
                parameters.append(TemplateParameter(
                    name,
                    default
                ))
            case ast.AnnAssign(
                target=ast.Name(id=name),
                annotation=ast.Name(id=type)|ast.Constant(value=type),
                value=ast.Name(id=default)|ast.Constant(value=default)
            ):
                parameters.append(TemplateParameter(
                    name,
                    type if isinstance(type, str) else type.id,
                    default if default is not None else RequiredParameter()
                ))

    return parameters
