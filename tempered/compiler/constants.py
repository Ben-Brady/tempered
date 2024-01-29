import ast
import string
import typing_extensions as t
from .. import ast_utils

CSS_VARIABLE = "__css"
WITH_STYLES_PARAMETER = "with_styles"
OUTPUT_VARIABLE = "__html"
NAME_LOOKUP_VARIABLE = "_name_lookup"
REGISTER_GLOBAL_FUNC = "__register_global"
REGISTER_TEMPLATE_DECORATOR = "__register_template_name"
RESOLVE_FUNC = "__resolve"
KWARGS_VARIABLE = "context"


FILE_HEADER = ast_utils.parse(
    f"""
from __future__ import annotations as _
from tempered._internals import escape as __escape
import typing_extensions as t

__globals = {{}}
{NAME_LOOKUP_VARIABLE} = {{}}

def {REGISTER_GLOBAL_FUNC}(name: str, value: t.Any):
    __globals[name] = value

def {REGISTER_TEMPLATE_DECORATOR}(name: str):
    def wrapper(func):
        {NAME_LOOKUP_VARIABLE}[name] = func
        return func

    return wrapper

def {RESOLVE_FUNC}(name: str, context: dict[str, t.Any]) -> t.Any:
    if name in context:
        return context[name]
    elif name in __globals:
        return __globals[name]
    else:
        raise RuntimeError(f"The variable '{{name}}' could not be resolved")
""")


def create_escape_call(value: ast.expr) -> ast.expr:
    return ast_utils.Call(func=ast_utils.Name("__escape"), arguments=[value])


def component_func_name(template_name: str) -> str:
    return "__" + filter_non_ident_chars(template_name)


def layout_func_name(template_name: str) -> str:
    template_name = filter_non_ident_chars(template_name)
    return f"__{template_name}_layout"


def template_func_name(template_name: str, is_layout: bool) -> str:
    if is_layout:
        return layout_func_name(template_name)
    else:
        return component_func_name(template_name)


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


def filter_non_ident_chars(name: str) -> str:
    IDENT_CHARS = string.ascii_letters + string.digits + "_"

    def encode_char(char: str) -> str:
        if char in IDENT_CHARS:
            return char
        else:
            code = ord(char)
            return f"_{hex(code)[2:]}_"

    return "".join(map(encode_char, name))


def create_resolve_call(name: str):
    return ast_utils.Call(
        func=ast_utils.Name(RESOLVE_FUNC),
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
