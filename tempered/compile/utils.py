import ast
from ..ast_utils import *

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

def create_escape_call(value: ast.expr) -> ast.expr:
    ESCAPE_FUNC_NAME = ast.Attribute(
        value=ast.Name(id='__internals'),
        attr='escape',
    )
    return create_call(ESCAPE_FUNC_NAME, [value])


def create_style_name(template_name: str) -> ast.Name:
    return create_name("__STYLE_" + template_name.upper())


def create_component_name(template_name: str) -> ast.Name:
    return ast.Name(id=template_name)

def create_layout_name(template_name: str) -> ast.Name:
    return ast.Name(id=template_name+"_layout")
