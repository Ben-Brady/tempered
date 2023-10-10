from .template import RequiredParameter, TemplateParameter, Template
from .parse import parse_template
from .construct import create_module, create_template_function
import ast
import astor
import inspect
import importlib
from pathlib import Path
from types import ModuleType
from typing import LiteralString, Any, cast
import autopep8


_type_imports: list[ast.ImportFrom] = []
_template_functions: list[ast.FunctionDef] = []


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
    template_data = parse_template(name, template, context)
    _template_func = create_template_function(template_data)
    _template_functions.append(_template_func)


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


def build():
    file_ast = create_module(
        type_imports=_type_imports,
        template_functions=_template_functions,
    )

    source = astor.to_source(file_ast)
    source = autopep8.fix_code(source)
    MODULE_FOLDER = Path(__file__).parent
    moudle_file = MODULE_FOLDER.joinpath(COMPONENTS_FILENAME)
    with open(moudle_file, "w") as f:
        f.write(source)

    return load_module()

COMPONENTS_FILENAME = "__components.py"
def load_module():
    from tempered import __components # type: ignore
    importlib.reload(__components)
    return __components

