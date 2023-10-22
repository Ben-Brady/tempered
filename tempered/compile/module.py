from ..ast_utils import create_name, create_assignment, create_module, create_function, create_constant
from ..parser import Template
from .constants import IMPORTS, style_constant
from .template import construct_template_arguments, construct_body
import ast
from typing import Sequence


def compile_module(
        type_imports: Sequence[ast.Import | ast.ImportFrom],
        templates: Sequence[Template],
        ) -> ast.Module:
    style_constants = [
        create_assignment(
            target=style_constant(template.name),
            value=template.style,
        )
        for template in templates
    ]

    return create_module([
        *IMPORTS,
        *type_imports,
        *style_constants,
        *(
            create_template_function(template)
            for template in templates
        ),
    ])


def create_template_function(template: Template) -> ast.FunctionDef:
    return create_function(
        name=template.name,
        args=construct_template_arguments(template.parameters),
        body=construct_body(template),
        returns=create_name('str'),
    )
