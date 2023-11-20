from .. import ast_utils
from ..ast_utils import create_name, create_assignment, create_module, create_function
from ..parser import Template, TemplateParameter, RequiredParameter
from .utils import (
    IMPORTS,
    create_style_name,
    create_slot_param,
    create_component_func_name,
    create_layout_func_name,
    WITH_STYLES_PARAMETER,
    LAYOUT_CSS_PARAMETER,
)
from .body import construct_body
import ast
from typing import Sequence


def compile_module(
    templates: Sequence[Template],
) -> ast.Module:
    style_constants = [
        create_assignment(
            target=create_style_name(template.name),
            value=template.css,
        )
        for template in templates
    ]
    update_required_css(templates)

    functions = []
    for template in templates:
        if template.type == "layout":
            function_name = create_layout_func_name(template.name)
        else:
            function_name = create_component_func_name(template.name)

        kw_arguements = [*template.parameters]
        kw_arguements.append(TemplateParameter(
            name=WITH_STYLES_PARAMETER,
            type=ast_utils.create_name("bool"),
            default=ast_utils.create_constant(True),
        ))
        if template.type == "layout":
            kw_arguements.append(TemplateParameter(
                name=create_slot_param(None),
                type=ast_utils.create_name("str"),
                default=ast_utils.create_constant(""),
            ))
            kw_arguements.append(TemplateParameter(
                name=LAYOUT_CSS_PARAMETER,
                type=ast_utils.create_name("str"),
                default=ast_utils.create_constant(""),
            ))

        args = create_arguments(
            arguments=[],
            kw_arguments=kw_arguements,
        )
        func = create_function(
            name=function_name,
            args=args,
            body=construct_body(template),
            returns=create_name("str"),
        )
        functions.append(func)

    return create_module(
        [
            *IMPORTS,
            *style_constants,
            *functions,
        ]
    )


def create_arguments(
    arguments: list[TemplateParameter], kw_arguments: list[TemplateParameter]
) -> ast.arguments:
    def construct_default(param: TemplateParameter) -> ast.expr | None:
        if isinstance(param.default, RequiredParameter):
            return None
        else:
            return param.default

    def create_argument_list(
        parameters: list[TemplateParameter],
    ) -> tuple[list[ast.arg], list[ast.expr | None]]:
        args = [
            ast.arg(
                arg=param.name,
                annotation=param.type,
            )
            for param in parameters
        ]
        defaults = [construct_default(param) for param in parameters]
        return args, defaults

    args, defaults = create_argument_list(arguments)
    kw_args, kw_defaults = create_argument_list(kw_arguments)

    return ast.arguments(
        args=args,
        defaults=defaults,
        kwonlyargs=kw_args,
        kw_defaults=kw_defaults,
        posonlyargs=[],
    )


def update_required_css(templates: Sequence[Template]):
    lookup = {template.name: template for template in templates}
    checked = set()

    def update(template: Template):
        if template.name in checked:
            return

        checked.add(template.name)
        children = set()
        children.update(template.child_components)
        for child_name in list(template.child_components):
            child = lookup[child_name]
            update(child)
            children.update(child.child_components)

        template.child_components = list(children)

    for template in templates:
        update(template)
