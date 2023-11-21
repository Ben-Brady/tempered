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
from .tag import construct_tag, BuildContext
from .accumulators import StringResult
from .utils import create_style_name, create_layout_call, COMPONENT_STYLES, LAYOUT_CSS_PARAMETER
import ast
from typing import Sequence, Any


def create_template_function(template: Template):
    arguements = [*template.parameters]
    arguements.append(
        TemplateParameter(
            name=WITH_STYLES_PARAMETER,
            type=ast_utils.Name("bool"),
            default=ast_utils.Constant(True),
        )
    )

    if template.type == "component":
        function_name = create_component_func_name(template.name)
    else:
        function_name = create_layout_func_name(
            template.name)
        arguements.append(
            TemplateParameter(
                name=LAYOUT_CSS_PARAMETER,
                type=ast_utils.Name("str"),
                default=ast_utils.Constant(""),
            )
        )
        for slot in template.slots:
            arguements.append(
                TemplateParameter(
                    name=create_slot_param(slot.name),
                    type=ast_utils.Name("str"),
                    default=ast_utils.Constant(slot.default),
                )
            )

    return ast_utils.Function(
        name=function_name,
        args=construct_arguments(arguements),
        body=construct_body(template),
        returns=ast_utils.Name("str"),
    )


def construct_arguments(arguments: list[TemplateParameter]) -> ast.arguments:
    args = []
    defaults = []
    for arguement in arguments:
        args.append(ast.arg(
            arg=arguement.name,
            annotation=arguement.type,
        ))
        defaults.append(arguement.default)

    return ast.arguments(
        kwonlyargs=args,
        kw_defaults=defaults,
        args=[],
        defaults=[],
        posonlyargs=[],
    )


def construct_body(template: Template) -> Sequence[ast.AST]:
    ctx = BuildContext(
        template=template,
        result=StringResult(),
    )

    statements: list[ast.AST] = []
    statements.extend(create_constants_variables(template.context))
    statements.extend(create_style_constant(ctx))
    statements.extend(ctx.result.create_assignment())
    for block in template.body:
        statements.extend(construct_tag(block, ctx))

    output_value = ctx.result.create_build()
    if template.layout is not None:
        output_value = create_layout_call(
            layout=template.layout,
            css=ast_utils.Name(COMPONENT_STYLES),
            html=output_value,
            slot=None,
        )

    statements.append(ast_utils.Return(output_value))
    return statements


def create_constants_variables(context: dict[str, Any]) -> list[ast.Assign]:
    statements = []
    for name, value in context.items():
        if name.startswith("__"):
            raise ValueError("Template context names cannot start with '__'")
        if name == "with_styles":
            raise ValueError("Template context names cannot be 'with_styles'")

        statements.append(ast_utils.Assignment(name, value))

    return statements


def create_style_constant(ctx: BuildContext):
    css_constants: list[ast.Name] = []
    css_constants.append(create_style_name(ctx.template.name))
    for name in ctx.template.child_components:
        css_constants.append(create_style_name(name))

    if ctx.template.type == "layout":
        css_constants.append(ast_utils.Name(LAYOUT_CSS_PARAMETER))

    return [ast_utils.If(
        condition=ast_utils.Name("with_styles"),
        if_body=[
            ast_utils.Assignment(
                COMPONENT_STYLES,
                ast_utils.StringConcat(*css_constants),
            )
        ],
        else_body=[
            ast_utils.Assignment(
                COMPONENT_STYLES,
                ast_utils.Constant(""),
            )
        ],
    )]
