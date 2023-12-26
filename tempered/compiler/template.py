from .. import ast_utils
from ..parser import Template, LayoutTemplate, TemplateParameter
from .utils import (
    slot_parameter,
    component_func_name,
    layout_func_name,
    create_layout_call,
    WITH_STYLES_PARAMETER,
    OUTPUT_VARIABLE,
    KWARGS_VARIABLE,
    CSS_VARIABLE,
)
from .resolve import create_resolve_for_unknown_variables
from .builder import CodeBuilder
from .accumulators import Variable
import ast
import typing_extensions as t


def create_template_function(
    template: Template,
    layout: t.Union[LayoutTemplate, None],
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
                name=CSS_VARIABLE,
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

    ctx = CodeBuilder(
        template=template,
        variable=Variable(OUTPUT_VARIABLE),
        layout=layout,
        css=css if len(css) > 0 else None,
    )
    func = ast_utils.Function(
        name=function_name,
        args=construct_arguments(arguements),
        body=construct_body(ctx),
        returns=ast_utils.Name("str"),
    )

    parameter_names = [param.name for param in ctx.template.parameters]
    component_names = [comp.component_name for comp in ctx.template.components_calls]
    create_resolve_for_unknown_variables(func.body, [*parameter_names, *component_names])
    ast.fix_missing_locations(func)
    return func


def construct_arguments(arguments: t.List[TemplateParameter]) -> ast.arguments:
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

    return ast_utils.Arguments(
        kwonlyargs=args,
        kw_defaults=defaults,
        kwarg=ast.arg(
            arg=KWARGS_VARIABLE,
            annotation=ast_utils.create("t.Any"),
        ),
    )


def construct_body(ctx: CodeBuilder) -> t.Sequence[ast.AST]:
    statements: t.List[ast.AST] = []
    if ctx.is_layout or ctx.uses_layout:
        statements.extend(create_style_contant(ctx))

    for tag in ctx.template.body:
        ctx.construct_tag(tag)

    ctx.ensure_assigned()
    output_value = ctx.variable.name

    statements.extend(ctx.body)

    if ctx.layout:
        output_value = create_layout_call(
            layout_name=ctx.layout.name,
            default_slot=output_value,
            css=ast_utils.Name(CSS_VARIABLE),
            has_default_slot=ctx.layout.has_default_slot,
            blocks=ctx.template.blocks,
        )

    statements.append(ast_utils.Return(output_value))
    return statements


def create_style_contant(ctx: CodeBuilder) -> t.List[ast.stmt]:
    if ctx.is_layout:
        value = ast_utils.Add(
            ast_utils.Name(CSS_VARIABLE),
            ast_utils.Constant(ctx.css or ""),
        )
    elif ctx.css is not None or ctx.uses_layout:
        value = ast_utils.Constant(ctx.css or "")
    else:
        return []

    return [ast_utils.Assign(target=CSS_VARIABLE, value=value)]
