from . import parse
from .compile import compile_module
from .parse import Template
import ast
import astor
import inspect
import importlib
from pathlib import Path
from typing import LiteralString, Any, cast
from types import ModuleType
import autopep8


_type_imports: list[ast.ImportFrom] = []
_templates: list[Template] = []


def add_template_folder(
        folder: Path|str,
        context: dict[str, Any] = {}
        ):
    folder = Path(folder)
    for file in folder.iterdir():
        if not file.name.endswith(".html"):
            continue

        name = file.name.removesuffix(".html")
        template = cast(LiteralString, file.read_text())
        add_template(
            name=name,
            template=template,
            context=context
        )


def add_template(
        name: str, template: LiteralString,
        *,
        context: dict[str, Any] = {}
        ):
    _templates.append(parse.parse_template(name, template, context))


def add_template_obj(template: Template):
    _templates.append(template)


def register_type(type: type):
    filepath = inspect.getfile(type)
    module = inspect.getmodulename(filepath)
    name = type.__name__
    import_ = ast.ImportFrom(
        module=module,
        names=[ast.alias(name=name)],
        level=0,
    )
    _type_imports.append(import_)



BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


def build():
    file_ast = compile_module(
        type_imports=_type_imports,
        templates=_templates,
    )

    source = astor.to_source(file_ast)
    source = autopep8.fix_code(source)

    with open(BUILD_FILE, "w") as f:
        f.write(source)

    return load()


def load():
    try:
        from tempered.generated import __components # type: ignore
    except Exception as e:
        BUILD_FILE.unlink(missing_ok=True)
        BUILD_FILE.touch()
        return load()
    else:
        importlib.reload(__components)
        return __components
