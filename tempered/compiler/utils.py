import ast
from .. import ast_utils
import typing_extensions as t


CSS_VARIABLE = "__css"
WITH_STYLES_PARAMETER = "with_styles"
OUTPUT_VARIABLE = "__html"
KWARGS_VARIABLE = "context"


FILE_HEADER = ast.parse(
    f"""
from __future__ import annotations as _
from tempered._internals import escape as __escape
import typing_extensions as t

__globals = {{}}

def reigster_global(name: str, value: t.Any):
    __globals[name] = value

def __resolve(name: str, context: dict[str, t.Any]) -> t.Any:
    if name in context:
        return context[name]
    elif name in __globals:
        return __globals[name]
    else:
        raise RuntimeError(f"The variable {{name}} could not be resolved")
"""
).body


def create_escape_call(value: ast.expr) -> ast.expr:
    return ast_utils.Call(func=ast_utils.Name("__escape"), arguments=[value])


def component_func_name(template_name: str) -> str:
    return template_name


def slot_variable_name(slot_name: t.Union[str, None]) -> str:
    if slot_name is None:
        return OUTPUT_VARIABLE
    else:
        return f"__{slot_name}_slot"


def slot_parameter(slot_name: t.Union[str, None]) -> str:
    if slot_name:
        return f"__slot_{slot_name}"
    else:
        return "__slot_default"


def layout_func_name(template_name: str) -> str:
    return f"__{template_name}_layout"


def create_resolve_call(name: str):
    return ast_utils.Call(
        func=ast_utils.Name("__resolve"),
        arguments=[
            ast_utils.Constant(name),
            ast_utils.Name(KWARGS_VARIABLE),
        ],
    )


def create_layout_call(
    layout_name: str,
    default_slot: ast.expr,
    css: ast.expr,
    has_default_slot: bool,
    blocks: t.Set[str],
) -> ast.expr:
    kw_args: t.Dict[str, ast.expr] = {}
    kw_args[CSS_VARIABLE] = css
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
