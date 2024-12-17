import ast
import string
import typing_extensions as t
from .. import ast_utils
from . import constants


def create_escape_call(value: ast.expr) -> ast.expr:
    return ast_utils.Call(
        func=ast_utils.Name(constants.ESCAPE_FUNC),
        arguments=[value],
    )


def component_func_name(template_name: str) -> str:
    return "__" + filter_non_ident_chars(template_name)


def layout_func_name(template_name: str) -> str:
    template_name = filter_non_ident_chars(template_name)
    return f"__{template_name}_layout"


def slot_variable_name(slot_name: t.Union[str, None]) -> str:
    if slot_name is None:
        return constants.OUTPUT_VAR
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
            return f"H{hex(code)[2:]}"

    return "".join(map(encode_char, name))


def create_resolve_call(name: str):
    return ast_utils.Call(
        func=ast_utils.Name(constants.RESOLVE_FUNC),
        arguments=[
            ast_utils.Constant(name),
            ast_utils.Name(constants.KWARGS_VAR),
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
    kw_args[constants.CSS_VARIABLE] = css
    kw_args[constants.WITH_STYLES] = ast_utils.Name(constants.WITH_STYLES)

    if has_default_slot:
        kw_args[slot_parameter(None)] = default_slot

    for slot in blocks:
        kw_args[slot_parameter(slot)] = ast_utils.Name(slot_variable_name(slot))

    return ast_utils.Call(
        func=ast_utils.Name(layout_func_name(layout_name)),
        keywords=kw_args,
        kwargs=ast_utils.Name(constants.KWARGS_VAR),
    )
