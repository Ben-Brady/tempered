import ast
import string
from copy import deepcopy
from pathlib import Path
import typing_extensions as t
from . import ast_utils, parser

ORIGINAL_FILE = Path(__file__).parent.joinpath("enviroment.py")
TYPES_FILE = ORIGINAL_FILE.with_suffix(".pyi")
T_OVERLOAD = ast_utils.create_expr("t.overload")


def clear_types() -> None:
    if TYPES_FILE.exists():
        TYPES_FILE.unlink()


def build_types(templates: t.List[parser.Template]) -> None:
    with open(ORIGINAL_FILE) as f:
        source = f.read()

    body = ast_utils.parse(source)

    template_classes = [create_template_class(template, body) for template in templates]
    body.extend(template_classes)

    get_template_overloads = [
        create_get_template_overload(template) for template in templates
    ]

    enviroment = find_class(body, "Environment")
    override_enviroment(enviroment, get_template_overloads)

    source = ast_utils.unparse(ast_utils.Module(body))
    TYPES_FILE.write_text(source)


def find_class(body: t.List[ast.stmt], name: str) -> ast.ClassDef:
    for node in body:
        if isinstance(node, ast.ClassDef):
            if node.name == name:
                return node

    raise RuntimeError("Could not find Environment class")


def create_get_template_overload(template: parser.Template) -> ast.FunctionDef:
    """Creates
    ```python
    def get_template(self, name: Literal["foo.html"]) -> _FooTemplate:
        ...
    ```
    """
    class_name = create_template_class_name(template)

    func_def = ast_utils.create_stmt(
        "def get_template(self, name: str) -> t.Optional[Template]: ...",
        ast.FunctionDef,
    )
    name_arg = func_def.args.args[1]
    name_arg.annotation = create_t_literal(template.name)
    func_def.returns = ast_utils.Name(class_name)
    func_def.decorator_list = [T_OVERLOAD]
    return func_def


def create_template_class(
    template: parser.Template, body: t.List[ast.stmt]
) -> ast.ClassDef:
    """Creates an object similar to this
    ```python
    class _ExampleTemplate
        def render(self, *, foo: str, bar: str, context: t.Any)
    ```"""

    class_def = deepcopy(find_class(body, "Template"))
    class_def.name = create_template_class_name(template)
    template_params = [
        ast_utils.Arg(param.name, param.type) for param in template.parameters
    ]
    param_defaults = [param.default for param in template.parameters]
    render_func = t.cast(ast.FunctionDef, class_def.body[0])
    render_func.args = ast_utils.Arguments(
        args=[ast_utils.Arg("self")],
        kwonlyargs=template_params,
        kw_defaults=param_defaults,
        kwarg=ast_utils.Arg("context", ast_utils.Name("t.Any")),
    )
    return class_def


def override_enviroment(enviroment: ast.ClassDef, overloads: t.List[ast.FunctionDef]):
    GET_TEMPLATE_NONE_OVERLOAD = ast_utils.create_stmt(
        "def get_template(self, name: str) -> None: ...",
        ast.FunctionDef,
    )
    GET_TEMPLATE_NONE_OVERLOAD.decorator_list = [T_OVERLOAD]

    for overload in overloads:
        enviroment.body.insert(0, overload)

    enviroment.body.insert(0, GET_TEMPLATE_NONE_OVERLOAD)


def create_t_literal(value: str) -> ast.expr:
    return ast_utils.Index(
        ast_utils.create_expr("t.Literal"),
        ast_utils.Constant(value),
    )


def create_template_class_name(template: parser.Template) -> str:
    IDENT_CHARS = string.ascii_letters + string.digits + "_"
    template_ident = "".join(ch for ch in template.name if ch in IDENT_CHARS)
    return f"_{template_ident}Template"
