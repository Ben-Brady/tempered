from .. import ast_utils, validate
from ..parser import Template, LayoutTemplate
from .utils import FILE_HEADER
from . import preprocess
from .template import create_template_function
import ast
from typing import Sequence


def compile_module(
    templates: Sequence[Template],
) -> ast.Module:
    validate.validate_templates(templates)

    lookup = {
        template.name: template
        for template in templates
    }
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
        func = create_template_function(template, layout, css)
        functions.append(func)

    return ast_utils.Module([
        *FILE_HEADER,
        *functions,
    ])
