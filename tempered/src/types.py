"This is a seperate file in order to generate custom types"
import ast
from pathlib import Path
from threading import Lock, Thread
import typing_extensions as t
from . import parsing
from .utils import ast_utils
from .utils.find import find

ORIGINAL_FILE = Path(__file__).parent.joinpath("tempered.py")
TYPES_FILE = ORIGINAL_FILE.with_suffix(".pyi")
file_lock = Lock()


def clear_types() -> None:
    def inner():
        file_lock.acquire(blocking=True)
        try:
            TYPES_FILE.unlink()
        except Exception:
            pass
        finally:
            file_lock.release()

    thread = Thread(target=inner)
    thread.daemon = True
    thread.start()


def build_types(templates: t.List[parsing.Template]) -> None:
    def inner():
        source = ORIGINAL_FILE.read_text()
        body = ast_utils.parse(source)
        module = ast_utils.Module(body)

        render_func_overloads = [
            create_render_func_overload(template) for template in templates
        ]
        insert_render_overloads(module, render_func_overloads)
        remove_function_bodys(module)

        source = ast_utils.unparse(module)

        file_lock.acquire(blocking=True)
        try:
            TYPES_FILE.write_text(source)
        finally:
            file_lock.release()

    thread = Thread(target=inner)
    thread.daemon = True
    thread.start()


def insert_render_overloads(
    module: ast.Module,
    render_func_overloads: "list[ast.FunctionDef]",
):
    if len(render_func_overloads) == 0:
        return

    class_def = find(
        module.body, type=ast.ClassDef, condition=lambda node: node.name == "Tempered"
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

    index = class_def.body.index(render_func)
    class_def.body.insert(index, default_render_func)


def create_render_func_overload(template: parsing.Template) -> ast.FunctionDef:
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
            ast_utils.Arg(param.name, param.type) for param in template.parameters
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
