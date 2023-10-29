from .. import ast_utils
from ..parser import Template
from .tag import construct_tag, BuildContext, StyleBlock
from .accumulators import StringResult
import ast
from typing import Sequence, Any

def construct_body(template: Template) -> Sequence[ast.AST]:
    add_default_style_block(template)

    statements: list[ast.AST] = []
    statements.extend(create_constants_variables(template.context))

    ctx = BuildContext(
        template=template,
        result=StringResult(),
    )

    statements.extend(ctx.result.create_assignment())
    for block in template.body:
        statements.extend(construct_tag(block, ctx))
    statements.append(ast_utils.create_return(
        value=ctx.result.create_build()
    ))
    return statements


def create_constants_variables(context: dict[str, Any]) -> list[ast.expr]:
    statements = []
    for name, value in context.items():
        if name.startswith("__"):
            raise ValueError("Template context names cannot start with '__'")
        if name == "with_styles":
            raise ValueError("Template context names cannot be 'with_styles'")

        statements.append(ast_utils.create_assignment(name, value))

    return statements


def add_default_style_block(template: Template):
    template_style_tag_count = len([t for t in template.body if isinstance(t, StyleBlock)])
    if template_style_tag_count > 1:
        raise ValueError("Templates can only have one style block")

    has_styles = template.css != "" or len(template.child_components) > 0
    if template_style_tag_count == 0 and has_styles:
        template.body = [StyleBlock(), *template.body]
