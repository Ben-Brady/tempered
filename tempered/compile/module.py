from .. import ast_utils
from ..ast_utils import create_name, create_assignment, create_module, create_function
from ..parser import Template, TemplateParameter, RequiredParameter
from .utils import IMPORTS, create_style_name
from .body import construct_body
import ast
from typing import Sequence


def compile_module(
        type_imports: Sequence[ast.Import | ast.ImportFrom],
        templates: Sequence[Template],
        ) -> ast.Module:
    style_constants = [
        create_assignment(
            target=create_style_name(template.name),
            value=template.css,
        )
        for template in templates
    ]

    functions = []
    for template in templates:
        args = create_arguments(
            arguments=[],
            kw_arguments=[
                *template.parameters,
                TemplateParameter(
                    name="with_styles",
                    type=ast_utils.create_name("bool"),
                    default=ast_utils.create_constant("True"),
                )
            ]
        )
        func = create_function(
            name=template.name,
            args=args,
            body=construct_body(template),
            returns=create_name('str'),
        )
        functions.append(func)


    return create_module([
        *IMPORTS,
        *type_imports,
        *style_constants,
        *functions,
    ])


def create_arguments(
        arguments: list[TemplateParameter],
        kw_arguments: list[TemplateParameter]
        ) -> ast.arguments:
    def construct_default(param: TemplateParameter) -> ast.expr | None:
        if isinstance(param.default, RequiredParameter):
            return None
        else:
            return param.default

    def create_argument_list(
            parameters: list[TemplateParameter]
            ) -> tuple[list[ast.arg], list[ast.expr | None]]:
        args = [
            ast.arg(
                arg=param.name,
                annotation=param.type,
            ) for param in parameters
        ]
        defaults = [construct_default(param) for param in parameters]
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
