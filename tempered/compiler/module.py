import ast
import typing_extensions as t
from .. import ast_utils, parser
from . import constants, preprocess, validate
from .template import create_template_function


def default_module_code() -> str:
    return constants.FILE_HEADER


def create_template_functions_code(
    templates: t.List[parser.Template],
    existing_templates: t.List[parser.Template],
) -> str:
    all_templates = [*templates, *existing_templates]

    validate.validate_templates(all_templates)
    lookup = {template.name: template for template in all_templates}
    layout_lookup = {
        template.name: template
        for template in all_templates
        if isinstance(template, parser.LayoutTemplate)
    }

    functions: t.List[ast.FunctionDef] = []
    for template in templates:
        if template.layout is None:
            layout = None
        else:
            layout = layout_lookup[template.layout]

        css = preprocess.generate_css(template, lookup)
        func = create_template_function(template, layout, css)
        functions.append(func)

    output_module = ast_utils.Module(functions)
    source = ast_utils.unparse(output_module)
    return source
