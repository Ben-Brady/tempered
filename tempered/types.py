"This is a seperate file in order to generate custom types"
import ast
from pathlib import Path
import typing_extensions as t
from . import ast_utils, parser

ORIGINAL_FILE = Path(__file__).parent.joinpath("tempered.py")
TYPES_FILE = ORIGINAL_FILE.with_suffix(".pyi")


def clear_types() -> None:
    try:
        TYPES_FILE.unlink()
    except Exception:
        pass


def build_types(templates: t.List[parser.Template]) -> None:
    source = ORIGINAL_FILE.read_text()
    body = ast_utils.parse(source)
    module = ast_utils.Module(body)

    render_func_overloads = [
        create_render_func_overload(template)
        for template in templates
    ]
    insert_render_overloads(module, render_func_overloads)
    remove_function_bodys(module)

    source = ast_utils.unparse(module)
    TYPES_FILE.write_text(source)

def insert_render_overloads(
    module: ast.Module,
    render_func_overloads: "list[ast.FunctionDef]",
    ):
    if len(render_func_overloads) == 0:
        return

    index = 0
    class_def = find(
        module.body,
        type=ast.ClassDef,
        condition=lambda node: node.name == "TemperedInterface"
    )
    render_func = find(
        class_def.body,
        type=ast.FunctionDef,
        condition=lambda node: node.name == "render",
    )

    default_render_func = ast_utils.copy(render_func)
    T_OVERLOAD = ast_utils.create_expr("t.overload")
    default_render_func.decorator_list = [T_OVERLOAD]

    for overload in render_func_overloads:
        index = class_def.body.index(render_func)
        class_def.body.insert(index, overload)

T = t.TypeVar("T", infer_variance=True)
def find(array: t.Iterable[t.Any], type: t.Type[T], condition: t.Callable[[T], bool]) -> T:
    for item in array:
        if isinstance(item, type) and condition(item):
            return item

    raise ValueError("Item not found")

def create_render_func_overload(template: parser.Template) -> ast.FunctionDef:
    def create_t_literal(value: str) -> ast.expr:
        return ast_utils.Index(
            ast_utils.create_expr("t.Literal"),
            ast_utils.Constant(value),
        )

    func_def = ast_utils.create_stmt(
        """
        @t.overload
        def render() -> str:
            ...
        """,
        ast.FunctionDef,
    )

    func_def.args = ast_utils.Arguments(
        args=[
            ast_utils.Arg("self"),
            ast_utils.Arg("name", create_t_literal(template.name)),
        ],
        kwonlyargs=[
            ast_utils.Arg(param.name, param.type)
            for param in template.parameters
        ],
        kw_defaults=[param.default for param in template.parameters],
        kwarg=ast_utils.Arg("context", ast_utils.Name("t.Any")),
    )
    return func_def


def remove_function_bodys(module: ast.Module):

    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef):
            ellipsis = ast_utils.create_stmt("...", ast.Expr)
            node.body = [ellipsis]
