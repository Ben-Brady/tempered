import ast

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

ESCAPE_FUNC_NAME = ast.Attribute(
    value=ast.Name(id='__internals'),
    attr='escape',
)


def style_constant(template_name: str) -> ast.Name:
    return ast.Name(
        id="__STYLE_" + template_name.upper()
    )
