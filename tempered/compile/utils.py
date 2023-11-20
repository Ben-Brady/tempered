import ast
from .. import ast_utils


UTILS_IMPORT = ast.ImportFrom(
    module='tempered',
    names=[ast.alias(
        name='_internals',
        asname='__internals'
    )],
    level=0
)


ANNOTATIONS_IMPORT = ast.ImportFrom(
    module='__future__',
    names=[ast.alias(name='annotations')],
    level=0,
)

IMPORTS = [
    ANNOTATIONS_IMPORT,
    UTILS_IMPORT,
]


WITH_STYLES_PARAMETER = "with_styles"
COMPONENT_STYLES = "__css"
LAYOUT_CSS_PARAMETER = "__component_css"


def create_escape_call(value: ast.expr) -> ast.expr:
    ESCAPE_FUNC_NAME = ast.Attribute(
        value=ast.Name(id='__internals'),
        attr='escape',
    )
    return ast_utils.create_call(ESCAPE_FUNC_NAME, [value])


def create_style_name(template_name: str) -> ast.Name:
    name = "STYLE_" + template_name.upper()
    return ast_utils.create_name(name)


def create_component_func_name(template_name: str) -> str:
    return template_name


def create_layout_func_name(template_name: str) -> str:
    return f"_{template_name}_layout"


def create_slot_param(slot_name: str | None) -> str:

    if slot_name:
        return f"_{slot_name}_slot"
    else:
        return "_default_slot"


def create_layout_call(html: ast.expr, css: ast.expr, layout: str, slot: str | None) -> ast.expr:
    return ast_utils.create_call(
        func=ast_utils.create_name(create_layout_func_name(layout)),
        keywords={
            create_slot_param(slot): html,
            LAYOUT_CSS_PARAMETER: css,
        }
    )
