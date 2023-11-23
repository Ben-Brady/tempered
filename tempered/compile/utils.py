import ast
from .. import ast_utils


UTILS_IMPORT = ast.ImportFrom(
    module="tempered",
    names=[ast.alias(name="_internals", asname="__internals")],
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
OUTPUT_VARIABLE = "__output"
KWARGS_VARIABLE = "kwargs"


def create_escape_call(value: ast.expr) -> ast.expr:
    ESCAPE_FUNC_NAME = ast.Attribute(
        value=ast.Name(id="__internals"),
        attr="escape",
    )
    return ast_utils.Call(ESCAPE_FUNC_NAME, [value])


def component_func_name(template_name: str) -> str:
    return template_name


def layout_func_name(template_name: str) -> str:
    return f"__{template_name}_layout"


def slot_variable_name(slot_name: str | None) -> str:
    if slot_name is None:
        return OUTPUT_VARIABLE
    else:
        return f"__{slot_name}_slot_content"


def slot_parameter(slot_name: str | None) -> str:
    if slot_name:
        return f"__{slot_name}_slot"
    else:
        return "__default_slot"


def create_layout_call(
    layout_name: str,
    css: ast.expr,
    has_default_slot: bool,
    blocks: set[str],
) -> ast.expr:
    kw_args = {}
    kw_args[LAYOUT_CSS_PARAMETER] = css

    if has_default_slot:
        kw_args[slot_parameter(None)] = ast_utils.Name(OUTPUT_VARIABLE)

    for slot in blocks:
        kw_args[slot_parameter(slot)] = ast_utils.Name(slot_variable_name(slot))

    return ast_utils.Call(
        func=ast_utils.Name(layout_func_name(layout_name)),
        keywords=kw_args,
        kwargs=ast_utils.Name(KWARGS_VARIABLE),
    )
