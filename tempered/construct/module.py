from ..template import Template
from .constants import ANNOTATIONS_IMPORT, MARKUPSAFE_IMPORT, ESCAPE_FUNC
from .function import construct_body, construct_template_arguments
import ast
from typing import Sequence


def create_module(
        type_imports: Sequence[ast.Import | ast.ImportFrom],
        template_functions: Sequence[ast.FunctionDef],
        ) -> ast.Module:
    return ast.Module(
        body=[
            ANNOTATIONS_IMPORT,
            MARKUPSAFE_IMPORT,
            ESCAPE_FUNC,
            *type_imports,
            *template_functions,
        ],
        type_ignores=[],
    )


def create_template_function(template: Template) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=template.name,
        args=construct_template_arguments(template.parameters),
        body=construct_body(template),
        returns=ast.Name(id='str', ctx=ast.Load()),
        decorator_list=[],
        type_params=[],
    )
