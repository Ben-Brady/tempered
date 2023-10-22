from ..parser.parse_ast import TemplateParameter, Template
from .tag import construct_tag, BuildContext, StyleBlock
from .. import ast_utils
import ast
from typing import Sequence



def construct_template_arguments(
        parameters: list[TemplateParameter]
        ) -> ast.arguments:
    return ast_utils.create_arguments(
        arguments=[],
        kw_arguments=[
            *parameters,
            TemplateParameter(
                name="with_styles",
                type="bool",
                default=True,
            )
        ]
    )


def construct_body(template: Template) -> Sequence[ast.AST]:
    statements: list[ast.AST] = []
    ctx = BuildContext(
        template=template,
        result_value=ast_utils.create_name('__html'),
    )

    statements.append(ast_utils.create_assignment(
        target=ctx.result_value,
        value=""
    ))
    # Load template context
    for name, value in template.context.items():
        if name.startswith("__"):
            raise ValueError("Template context names cannot start with '__'")
        if name == "with_styles":
            raise ValueError("Template context names cannot be 'with_styles'")

        statements.append(ast_utils.create_assignment(name, value))

    template_style_tag_count = len([t for t in template.body if isinstance(t, StyleBlock)])
    if template_style_tag_count > 1:
        raise ValueError("Templates can only have one style block")

    has_styles = template.style != "" or len(template.child_components) > 0
    if template_style_tag_count == 0 and has_styles:
        template.body = [StyleBlock(), *template.body]

    for block in template.body:
        statements.extend(construct_tag(block, ctx))

    statements.append(ast.Return(
        value=ctx.result_value,
    ))
    return statements

