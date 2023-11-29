import ast
from .. import ast_utils


UTILS_IMPORT = ast.ImportFrom(
    module="tempered._internals",
    names=[ast.alias(name="escape", asname="__escape")],
    level=0,
)

TYPING_MODULE = "__typing"
TYPING_IMPORT = ast.Import(names=[ast.alias(name="typing", asname=TYPING_MODULE)])


ANNOTATIONS_IMPORT = ast.ImportFrom(
    module="__future__",
    names=[ast.alias(name="annotations", asname="__annotations")],
    level=0,
)

IMPORTS = [
    ANNOTATIONS_IMPORT,
    TYPING_IMPORT,
    UTILS_IMPORT,
]


WITH_STYLES_PARAMETER = "with_styles"
LAYOUT_CSS_PARAMETER = "__component_css"
COMPONENT_CSS_VARIABLE = "__css"
OUTPUT_VARIABLE = "__html"
KWARGS_VARIABLE = "kwargs"


def create_escape_call(value: ast.expr) -> ast.expr:
    ESCAPE_FUNC_NAME = ast.Name(id="__escape")
    return ast_utils.Call(ESCAPE_FUNC_NAME, [value])


def component_func_name(template_name: str) -> str:
    return template_name


def slot_variable_name(slot_name: str | None) -> str:
    if slot_name is None:
        return OUTPUT_VARIABLE
    else:
        return f"__slot_{slot_name}_content"


def slot_parameter(slot_name: str | None) -> str:
    if slot_name:
        return f"__slot_{slot_name}"
    else:
        return "__slot_default"


def layout_func_name(template_name: str) -> str:
    return f"__{template_name}_layout"


def create_layout_call(
    layout_name: str,
    default_slot: ast.expr,
    css: ast.expr,
    has_default_slot: bool,
    blocks: set[str],
) -> ast.expr:
    kw_args: dict[str, ast.expr] = {}
    kw_args[LAYOUT_CSS_PARAMETER] = css
    kw_args[WITH_STYLES_PARAMETER] = ast_utils.Name(WITH_STYLES_PARAMETER)

    if has_default_slot:
        kw_args[slot_parameter(None)] = default_slot

    for slot in blocks:
        kw_args[slot_parameter(slot)] = ast_utils.Name(slot_variable_name(slot))

    return ast_utils.Call(
        func=ast_utils.Name(layout_func_name(layout_name)),
        keywords=kw_args,
        kwargs=ast_utils.Name(KWARGS_VARIABLE),
    )
