import ast
import typing_extensions as t
from .. import ast_utils
from ..parser import LayoutTemplate, Template, TemplateParameter
from . import constants
from .accumulators import Variable
from .builder import BuildContext
from .calls import (
    component_func_name,
    create_layout_call,
    layout_func_name,
    slot_parameter,
)
from .resolve import create_resolve_for_unknown_variables
from .rules import default_rules


def create_template_function(
    template: Template,
    layout: t.Union[LayoutTemplate, None],
    css: str,
) -> ast.FunctionDef:
    arguements = [*template.parameters]
    arguements.append(
        TemplateParameter(
            name=constants.WITH_STYLES,
            type=ast_utils.Name("bool"),
            default=ast_utils.Constant(True),
        )
    )

    if not isinstance(template, LayoutTemplate):
        function_name = component_func_name(template.name)
    else:
        function_name = layout_func_name(template.name)
        arguements.append(
            TemplateParameter(
                name=constants.CSS_VARIABLE,
                type=ast_utils.Str,
            )
        )

        for slot in template.slots:
            if slot.is_required:
                type = ast_utils.Str
                default = None
            else:
                type = ast_utils.Union(ast_utils.Str, ast_utils.None_)
                default = ast_utils.Constant(None)

            arguements.append(
                TemplateParameter(
                    name=slot_parameter(slot.name),
                    type=type,
                    default=default,
                )
            )

    ctx = BuildContext(
        template=template,
        output_variable=Variable(constants.OUTPUT_VAR),
        layout=layout,
        css=css if len(css) > 0 else None,
        rules=default_rules,
    )
    func = ast_utils.Function(
        name=function_name,
        decorators=[create_register_template_decorator(template.name)],
        args=construct_arguments(arguements),
        body=construct_body(ctx),
        returns=ast_utils.Name("str"),
    )

    parameter_names = [param.name for param in ctx.template.parameters]
    component_names = [comp.component_name for comp in ctx.template.components_calls]
    create_resolve_for_unknown_variables(
        func.body, [*parameter_names, *component_names]
    )
    ast.fix_missing_locations(func)
    return func


def construct_arguments(arguments: t.List[TemplateParameter]) -> ast.arguments:
    args = []
    defaults = []
    for arguement in arguments:
        args.append(
            ast.arg(
                arg=arguement.name,
                annotation=None,
            )
        )
        defaults.append(arguement.default)

    return ast_utils.Arguments(
        kwonlyargs=args,
        kw_defaults=defaults,
        kwarg=ast_utils.Arg(
            name=constants.KWARGS_VAR,
            annotation=ast_utils.create_expr("t.Any"),
        ),
    )


def construct_body(ctx: BuildContext) -> t.Sequence[ast.AST]:
    statements: t.List[ast.AST] = []
    if ctx.is_layout or ctx.uses_layout:
        statements.extend(create_style_contant(ctx))

    for tag in ctx.template.body:
        ctx.construct_tag(tag)

    ctx.ensure_output_assigned()
    output_value = ctx.output_variable.name

    statements.extend(ctx.body)

    if ctx.layout:
        output_value = create_layout_call(
            layout_name=ctx.layout.name,
            default_slot=output_value,
            css=ast_utils.Name(constants.CSS_VARIABLE),
            has_default_slot=ctx.layout.has_default_slot,
            blocks=ctx.template.blocks,
        )

    statements.append(ast_utils.Return(output_value))
    return statements


def create_style_contant(ctx: BuildContext) -> t.List[ast.stmt]:
    if ctx.is_layout:
        return []

    if ctx.css is None and not ctx.uses_layout:
        return []

    value = ast_utils.Constant(ctx.css or "")

    ctx.css_variable = Variable(constants.CSS_VARIABLE)
    return ctx.css_variable.assign(value)


def create_register_template_decorator(name: str) -> ast.Call:
    return ast_utils.Call(
        ast_utils.Name(constants.REGISTER_TEMPLATE_NAME_DECORATOR), [ast.Str(name)]
    )
