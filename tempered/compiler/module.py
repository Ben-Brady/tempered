import ast
import typing_extensions as t
from types import ModuleType
from .. import ast_utils, parser
from ..css import finalise_css
from . import preprocess, validate, constants
from .template import create_template_function


def create_default_module_code() -> str:
    return constants.FILE_HEADER


def create_add_templates_code(
    templates: t.List[parser.Template],
    module: ModuleType,
) -> str:
    suplimental_templates = module.__dict__[constants.TEMPLATE_LIST_VAR]
    all_templates = [*templates, *suplimental_templates]

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
