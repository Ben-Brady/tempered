import ast
from typing import Sequence
from .. import ast_utils
from ..css import finalise_css
from ..parser import LayoutTemplate, Template
from . import preprocess, validate
from .constants import FILE_HEADER
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
    for template in templates:
        if template.layout is None:
            layout = None
        else:
            layout = layout_lookup[template.layout]

        css = preprocess.calculate_required_css(template, lookup)
        css = finalise_css(css)
        func = create_template_function(template, layout, css)
        functions.append(func)

    body = [
        *FILE_HEADER,
        *functions,
    ]
    return ast_utils.Module(body)
