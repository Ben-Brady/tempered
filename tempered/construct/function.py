from ..template import RequiredParameter, TemplateParameter, Template
from .tag import construct_tag
from .utils import value_to_constant
import ast
from typing import Sequence


def construct_template_arguments(
        parameters: list[TemplateParameter]
        ) -> ast.arguments:
    args = [
        ast.arg(
            arg=param.name,
            annotation=ast.Constant(value=param.type) if param.type else None,
        )
        for param in parameters
    ]

    def construct_default(param: TemplateParameter):
        match param.default:
            case RequiredParameter():
                return None
            case default:
                return value_to_constant(default)

    return ast.arguments(
        args=args,
        posonlyargs=[],
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[construct_default(param) for param in parameters],
    )


def construct_body(template: Template) -> Sequence[ast.AST]:
    statements: list[ast.AST] = []
    result_value = ast.Name(id='html', ctx=ast.Store())

    # Load template context
    for name, value in template.context.items():
        if name == 'html':
            raise ValueError("Cannot use 'html' as a template context name")

        statements.append(ast.Assign(
            targets=[ast.Name(id=name, ctx=ast.Store())],
            value=value_to_constant(value)
        ))

    statements.append(ast.Assign(
        targets=[result_value],
        value=ast.Constant(value="")
    ))

    for block in template.body:
        statements.extend(construct_tag(block, result_value))

    statements.append(ast.Return(
        value=result_value,
    ))
    return statements
