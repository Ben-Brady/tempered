"This is a seperate file in order to generate custom types"
import ast
from pathlib import Path
import typing_extensions as t
from . import ast_utils, parser

if t.TYPE_CHECKING:
    from .tempered import Tempered
else:
    Tempered = t.Any

ORIGINAL_FILE = Path(__file__).parent.joinpath("render.py")
TYPES_FILE = ORIGINAL_FILE.with_suffix(".pyi")


def render_template(self: Tempered, name: str, **context: t.Any) -> str:
    return self._render_template(name, **context)


def clear_types() -> None:
    if TYPES_FILE.exists():
        TYPES_FILE.unlink()


def build_types(templates: t.List[parser.Template]) -> None:
    with open(ORIGINAL_FILE) as f:
        source = f.read()

    body = ast_utils.parse(source)

    render_template_overloads = [
        create_render_template_overload(template) for template in templates
    ]

    # Insert render overloads, only if there are any
    if len(render_template_overloads) != 0:
        default_render_template = ast_utils.create_stmt(
            """
            @t.overload
            def render_template(self, template_name: str, **context: t.Any) -> str:
                ...
            """,
            ast.FunctionDef,
        )
        render_template_overloads.append(default_render_template)
        index = 0
        for index, node in enumerate(body):
            if isinstance(node, ast.FunctionDef) and node.name == "render_template":
                break

        for overload in render_template_overloads:
            body.insert(index, overload)
            index += 1

    for node in body:
        if isinstance(node, ast.FunctionDef):
            node.body = [ast_utils.create_stmt("...", ast.Expr)]

    source = ast_utils.unparse(ast_utils.Module(body))
    TYPES_FILE.write_text(source)


def create_render_template_overload(template: parser.Template) -> ast.FunctionDef:
    def create_t_literal(value: str) -> ast.expr:
        return ast_utils.Index(
            ast_utils.create_expr("t.Literal"),
            ast_utils.Constant(value),
        )

    func_def = ast_utils.create_stmt(
        """
        @t.overload
        def render_template() -> str:
            ...
        """,
        ast.FunctionDef,
    )
    func_def.args = ast_utils.Arguments(
        args=[
            ast_utils.Arg("self"),
            ast_utils.Arg("template_name", create_t_literal(template.name)),
        ],
        kwonlyargs=[
            ast_utils.Arg(param.name, param.type) for param in template.parameters
        ],
        kw_defaults=[param.default for param in template.parameters],
        kwarg=ast_utils.Arg("context", ast_utils.Name("t.Any")),
    )
    return func_def
