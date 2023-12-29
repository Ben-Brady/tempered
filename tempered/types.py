from . import parser, ast_utils
import ast
import string
import typing_extensions as t
from .compiler.utils import component_func_name
from pathlib import Path


TYPES_FILE = Path(__file__).parent.joinpath("enviroment.pyi")
T_OVERLOAD = ast_utils.create_expr("t.overload")


def clear_types() -> None:
    if TYPES_FILE.exists():
        TYPES_FILE.unlink()


def build_types(templates: t.List[parser.Template]) -> None:
    BASE = """
import typing_extensions as t
from dataclasses import dataclass

class Template:
    def render(self, **context: t.Any) -> str:
        pass
"""
    body = ast_utils.parse(BASE)

    template_overloads = []
    for template in templates:
        IDENT_CHARS = string.ascii_letters + string.digits + "_"
        template_ident = "".join(ch for ch in template.name if ch in IDENT_CHARS)
        class_name = f"_{template_ident}Template"

        class_def = create_template_class(template, class_name)
        overload = create_template_overload(template, class_name)
        body.append(class_def)
        template_overloads.append(overload)

    enviroment = create_enviroment(template_overloads)
    body.append(enviroment)
    source = ast_utils.unparse(ast_utils.Module(body))
    TYPES_FILE.write_text(source)


def create_template_overload(
    template: parser.Template, class_name: str
) -> ast.FunctionDef:
    """Creates
    ```python
    def get_template(self, name: Literal["foo.html"]) -> _FooTemplate:
        ...
    ```
    """

    def create_t_literal(value: str) -> ast.expr:
        return ast_utils.Index(
            ast_utils.create_expr("t.Literal"),
            ast_utils.Constant(value),
        )

    func_def = ast_utils.create_stmt(
        "def get_template(self, name: str) -> t.Optional[Template]: ...",
        ast.FunctionDef,
    )
    name_arg = func_def.args.args[1]
    name_arg.annotation = create_t_literal(template.name)
    func_def.returns = ast_utils.Name(class_name)
    func_def.decorator_list = [T_OVERLOAD]
    return func_def


def create_template_class(template: parser.Template, class_name: str) -> ast.ClassDef:
    """Creates an object similar to this
    ```python
    class _ExampleTemplate
        def render(self, *, foo: str, bar: str, context: t.Any)
    ```"""

    template_base = """
class Template:
    def render(self, **context: t.Any) -> str:
        ...
"""
    class_def = ast_utils.create_stmt(template_base, ast.ClassDef)
    class_def.name = class_name
    template_params = [
        ast_utils.Arg(param.name, param.type) for param in template.parameters
    ]
    param_defaults = [param.default for param in template.parameters]
    render_func = t.cast(ast.FunctionDef, class_def.body[0])
    render_func.args = ast_utils.Arguments(
        args=[
            ast_utils.Arg("self"),
        ],
        kwonlyargs=template_params,
        kw_defaults=param_defaults,
        kwarg=ast_utils.Arg("context", ast_utils.Name("t.Any")),
    )
    return class_def


def create_enviroment(overloads: t.List[ast.FunctionDef]) -> ast.ClassDef:
    enviroment_base = """
class Environment:
    def __init__(self, templates: t.Dict[str, Template], globals: t.Dict[str, t.Any]):
        ...

"""
    GET_TEMPLATE_NONE_OVERLOAD = ast_utils.create_stmt(
        "def get_template(self, name: str) -> None: ...",
        ast.FunctionDef,
    )
    GET_TEMPLATE_NONE_OVERLOAD.decorator_list = [T_OVERLOAD]

    GET_TEMPLATE = ast_utils.create_stmt(
        "def get_template(self, name: str) -> t.Optional[Template]: ...",
        ast.FunctionDef,
    )

    FROM_STRING = ast_utils.create_stmt(
        "def from_string(self, template: str) -> Template:...", ast.FunctionDef
    )
    enviroment = ast_utils.create_stmt(enviroment_base, ast.ClassDef)
    enviroment.body.extend(overloads)
    enviroment.body.append(GET_TEMPLATE_NONE_OVERLOAD)
    enviroment.body.append(GET_TEMPLATE)
    enviroment.body.append(FROM_STRING)
    return enviroment
