import ast
from typing import Sequence
from .. import ast_utils
from ..css import finalise_css
from ..parser import LayoutTemplate, Template
from . import preprocess, validate
from .constants import FILE_HEADER, NAME_LOOKUP_VARIABLE
from .template import create_template_function


def compile_module(
    templates: Sequence[Template],
) -> ast.Module:
    validate.validate_templates(templates)

    lookup = {template.name: template for template in templates}
    layout_lookup = {
        template.name: template
        for template in templates
        if isinstance(template, LayoutTemplate)
    }

    functions = []
    name_func_map = {}
    for template in templates:
        if template.layout is None:
            layout = None
        else:
            layout = layout_lookup[template.layout]

        css = preprocess.calculate_required_css(template, lookup)
        css = finalise_css(css)
        func = create_template_function(template, layout, css)
        name_func_map[template.name] = ast_utils.Name(func.name)
        functions.append(func)

    body = [
        *FILE_HEADER,
        *functions,
        ast_utils.Assign(NAME_LOOKUP_VARIABLE, ast_utils.Constant(name_func_map)),
    ]
    return ast_utils.Module(body)
