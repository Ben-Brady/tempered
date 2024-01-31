CSS_VARIABLE = "__css"
WITH_STYLES = "with_styles"
OUTPUT_VAR = "__html"
NAME_LOOKUP_VAR = "__name_lookup"
GLOBALS_VAR = "__globals"
TEMPLATE_LIST_VAR = "__templates"
REGISTER_TEMPLATE_FUNC = "__register_template"
REGISTER_GLOBAL_FUNC = "__register_global"
ESCAPE_FUNC = "__escape"
REGISTER_TEMPLATE_NAME_DECORATOR = "__register_template_name"
RESOLVE_FUNC = "__resolve"
KWARGS_VAR = "context"


FILE_HEADER = f"""
from __future__ import annotations as _
from tempered._internals import escape as {ESCAPE_FUNC}
from tempered import parser as __parser
import typing_extensions as t

{GLOBALS_VAR} = {{}}
{NAME_LOOKUP_VAR} = {{}}
{TEMPLATE_LIST_VAR} = []

def {REGISTER_GLOBAL_FUNC}(name: str, value: t.Any):
    {GLOBALS_VAR}[name] = value

def {REGISTER_TEMPLATE_FUNC}(template: __parser.Template):
    {TEMPLATE_LIST_VAR}.append(template)


def {REGISTER_TEMPLATE_NAME_DECORATOR}(name: str):
    def wrapper(func):
        {NAME_LOOKUP_VAR}[name] = func
        return func

    return wrapper

def {RESOLVE_FUNC}(name: str, context: t.Dict[str, t.Any]) -> t.Any:
    if name in context:
        return context[name]
    elif name in {GLOBALS_VAR}:
        return {GLOBALS_VAR}[name]
    else:
        raise RuntimeError(f"The variable '{{name}}' could not be resolved")
"""
