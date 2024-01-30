import ast
from types import ModuleType
import typing_extensions as t
from .. import ast_utils, parser
from ..css import finalise_css
from . import constants, preprocess, validate
from .template import create_template_function


def create_default_module_code() -> str:
    return constants.FILE_HEADER


def create_add_templates_code(
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

        css = preprocess.calculate_required_css(template, lookup)
        css = finalise_css(css)
        func = create_template_function(template, layout, css)
        functions.append(func)

    register_calls: t.List[ast.Expr] = []
    for template in templates:
        register_call = ast_utils.Expr(
            ast_utils.Call(
                func=ast_utils.Name(constants.REGISTER_TEMPLATE_FUNC),
                arguments=[constants.create_pickled_obj(template)],
            )
        )
        register_calls.append(register_call)

    output_module = ast_utils.Module([*register_calls, *functions])
    source = ast_utils.unparse(output_module)
    return source
