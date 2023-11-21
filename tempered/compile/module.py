from .. import ast_utils
from ..parser import Template, LayoutTemplate, TemplateParameter
from .utils import IMPORTS, css_name
from .preprocess import update_template_nested_children
from .template import create_template_function
import ast
from typing import Sequence, cast


def compile_module(
    templates: Sequence[Template],
) -> ast.Module:
    style_constants = [
        ast_utils.Assign(
            target=css_name(template.name),
            value=template.css,
        )
        for template in templates
    ]
    update_template_nested_children(templates)

    template_lookup = {
        template.name: cast(LayoutTemplate, template)
        for template in templates
    }

    functions = []
    for template in templates:
        if template.layout is None:
            layout = None
        elif template.layout in template_lookup:
            layout = template_lookup[template.layout]
        else:
            raise ValueError(
                f"Template {template.name} using non-existant layout {template.layout}"
            )

        func = create_template_function(template, layout)
        functions.append(func)

    return ast_utils.Module([
        *IMPORTS,
        *style_constants,
        *functions,
    ])
