from .. import ast_utils
from ..parser import Template
from .tag import construct_tag, BuildContext
from .accumulators import StringResult
from .utils import create_style_name, create_layout_call, COMPONENT_STYLES, LAYOUT_CSS_PARAMETER
import ast
from typing import Sequence, Any


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
            css=ast_utils.create_name(COMPONENT_STYLES),
            html=output_value,
            slot=None,
        )

    statements.append(ast_utils.create_return(output_value))
    return statements


def create_constants_variables(context: dict[str, Any]) -> list[ast.Assign]:
    statements = []
    for name, value in context.items():
        if name.startswith("__"):
            raise ValueError("Template context names cannot start with '__'")
        if name == "with_styles":
            raise ValueError("Template context names cannot be 'with_styles'")

        statements.append(ast_utils.create_assignment(name, value))

    return statements


def create_style_constant(ctx: BuildContext):
    css_constants: list[ast.Name] = []
    css_constants.append(create_style_name(ctx.template.name))
    for name in ctx.template.child_components:
        css_constants.append(create_style_name(name))

    if ctx.template.type == "layout":
        css_constants.append(ast_utils.create_name(LAYOUT_CSS_PARAMETER))

    return [ast_utils.create_if(
        condition=ast_utils.create_name("with_styles"),
        if_body=[
            ast_utils.create_assignment(
                COMPONENT_STYLES,
                ast_utils.create_string_concat(*css_constants),
            )
        ],
        else_body=[
            ast_utils.create_assignment(
                COMPONENT_STYLES,
                ast_utils.create_constant(""),
            )
        ],
    )]
