from .. import ast_utils
from ..parser import Template, LayoutTemplate, TemplateParameter
from .utils import (
    slot_parameter,
    component_func_name,
    layout_func_name,
    create_layout_call,
    WITH_STYLES_PARAMETER,
    LAYOUT_CSS_PARAMETER,
    OUTPUT_VARIABLE,
    KWARGS_VARIABLE,
    COMPONENT_CSS_VARIABLE,
    TYPING_MODULE,
)
from .rename import convert_unknown_variables_to_kwargs
from .tag import construct_tag, BuildContext
from .accumulators import StringResult
import ast
from typing import Sequence, Any


def create_template_function(
    template: Template,
    layout: LayoutTemplate | None,
    css: str,
) -> ast.FunctionDef:
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

            arguements.append(
                TemplateParameter(
                    name=slot_parameter(slot.name),
                    type=type,
                    default=default,
                )
            )

    ctx = BuildContext(
        template=template,
        result=StringResult(OUTPUT_VARIABLE),
        layout=layout,
        css=css,
    )
    func = ast_utils.Function(
        name=function_name,
        args=construct_arguments(arguements),
        body=construct_body(ctx),
        returns=ast_utils.Name("str"),
    )

    parameter_names = [param.name for param in ctx.template.parameters]
    component_names = [comp.component_name for comp in ctx.template.components_calls]
    convert_unknown_variables_to_kwargs(func.body, [*parameter_names, *component_names])
    ast.fix_missing_locations(func)
    return func


def construct_arguments(arguments: list[TemplateParameter]) -> ast.arguments:
    args = []
    defaults = []
    for arguement in arguments:
        args.append(
            ast.arg(
                arg=arguement.name,
                annotation=arguement.type,
            )
        )
        defaults.append(arguement.default)

    return ast.arguments(
        kwonlyargs=args,
        kw_defaults=defaults,
        kwarg=ast.arg(
            arg=KWARGS_VARIABLE,
            annotation=ast_utils.Attribute(
                value=ast_utils.Name(TYPING_MODULE),
                attr="Any",
            ),
        ),
        args=[],
        defaults=[],
        posonlyargs=[],
    )


def construct_body(ctx: BuildContext) -> Sequence[ast.AST]:
    statements: list[ast.AST] = []
    statements.append(create_stlye_contant(ctx))
    statements.extend(ctx.result.create_init())

    for block in ctx.template.body:
        statements.extend(construct_tag(block, ctx))

    output_value = ctx.result.create_value()
    if ctx.layout is not None:
        output_value = create_layout_call(
            layout_name=ctx.layout.name,
            css=ast_utils.Name(COMPONENT_CSS_VARIABLE),
            has_default_slot=ctx.layout.has_default_slot,
            blocks=ctx.template.blocks,
        )

    statements.append(ast_utils.Return(output_value))
    return statements


def create_stlye_contant(ctx: BuildContext) -> ast.Assign:
    if isinstance(ctx.template, LayoutTemplate):
        if len(ctx.css) == 0:
            value = ast_utils.Name(LAYOUT_CSS_PARAMETER)
        else:
            value = ast_utils.Add(
                ast_utils.Constant(ctx.css),
                ast_utils.Name(LAYOUT_CSS_PARAMETER),
            )
    else:
        value = ast_utils.Constant(ctx.css)

    return ast_utils.Assign(target=COMPONENT_CSS_VARIABLE, value=value)
