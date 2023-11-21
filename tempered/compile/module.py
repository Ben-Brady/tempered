from .. import ast_utils
from ..parser import Template, TemplateParameter
from .utils import (
    IMPORTS,
    create_style_name,
    create_slot_param,
    create_component_func_name,
    create_layout_func_name,
    WITH_STYLES_PARAMETER,
    LAYOUT_CSS_PARAMETER,
)
from .preprocess import update_template_nested_children
from .template import create_template_function
import ast
from typing import Sequence


def compile_module(
    templates: Sequence[Template],
) -> ast.Module:
    style_constants = [
        ast_utils.Assignment(
            target=create_style_name(template.name),
            value=template.css,
        )
        for template in templates
    ]
    update_template_nested_children(templates)

    functions = [
        create_template_function(template)
        for template in templates
    ]

    return ast_utils.Module([
        *IMPORTS,
        *style_constants,
        *functions,
    ])
