from .. import ast_utils
from ..parser import Template, LayoutTemplate, TemplateParameter
from .utils import (
    css_name,
    slot_parameter,
    component_func_name,
    layout_func_name,
    IMPORTS,
    WITH_STYLES_PARAMETER,
    LAYOUT_CSS_PARAMETER,
    OUTPUT_VARIABLE,
)
from .tag import construct_tag, BuildContext
from .accumulators import StringResult
from .utils import css_name, create_layout_call, COMPONENT_STYLES, LAYOUT_CSS_PARAMETER
import ast
from typing import Sequence, Any


def create_template_function(template: Template, layout: LayoutTemplate | None):
    arguements = [*template.parameters]
    arguements.append(
        TemplateParameter(
            name=WITH_STYLES_PARAMETER,
            type=ast_utils.Name("bool"),
            default=ast_utils.True_,
        )
    )

    if not isinstance(template, LayoutTemplate):
        function_name = component_func_name(template.name)
    else:
        function_name = layout_func_name(template.name)
        arguements.append(
            TemplateParameter(
                name=LAYOUT_CSS_PARAMETER,
                type=ast_utils.Str,
            )
        )

        if template.has_default_slot:
            arguements.append(
                TemplateParameter(
                    name=slot_parameter(None),
                    type=ast_utils.Str,
                )
            )


        for slot in template.slots:
            if slot.default:
                type = ast_utils.Union(ast_utils.Str, ast_utils.None_)
                default = ast_utils.Constant(None)
            else:
                type = ast_utils.Str
                default = None

            arguements.append(TemplateParameter(
                name=slot_parameter(slot.name),
                type=type,
                default=default,
            ))


    return ast_utils.Function(
        name=function_name,
        args=construct_arguments(arguements),
        body=construct_body(template, layout),
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


def construct_body(template: Template, layout: LayoutTemplate|None = None) -> Sequence[ast.AST]:
    ctx = BuildContext(
        template=template,
        result=StringResult(OUTPUT_VARIABLE),
        layout=layout,
    )

    statements: list[ast.AST] = []
    statements.extend(create_constants_variables(template.context))
    statements.extend(create_style_constant(ctx))
    statements.extend(ctx.result.create_init())

    for block in template.body:
        statements.extend(construct_tag(block, ctx))

    output_value = ctx.result.create_value()
    if layout is not None:
        output_value = create_layout_call(
            layout_name=layout.name,
            css=ast_utils.Name(COMPONENT_STYLES),
            has_default_slot=layout.has_default_slot,
            blocks=template.blocks,
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

        statements.append(ast_utils.Assign(name, value))

    return statements


def create_style_constant(ctx: BuildContext):
    css_constants: list[ast.Name] = []
    css_constants.append(css_name(ctx.template.name))
    for name in ctx.template.child_components:
        css_constants.append(css_name(name))

    if isinstance(ctx.template, LayoutTemplate):
        css_constants.append(ast_utils.Name(LAYOUT_CSS_PARAMETER))

    return [ast_utils.If(
        condition=ast_utils.Name("with_styles"),
        if_body=[
            ast_utils.Assign(
                COMPONENT_STYLES,
                ast_utils.Add(*css_constants),
            )
        ],
        else_body=[
            ast_utils.Assign(
                COMPONENT_STYLES,
                ast_utils.Constant(""),
            )
        ],
    )]
