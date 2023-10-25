from . import parser
from .compile.module import compile_module
from .parser import Template
import ast
import sys
import inspect
import importlib
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import LiteralString, Any, cast
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
    template_obj = parser.parse_template(name, template, context)
    _templates.append(template_obj)


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


def _build_python() -> str:
    module_ast = compile_module(
        type_imports=_type_imports,
        templates=_templates,
    )
    _type_imports.clear()
    _templates.clear()
    return ast.unparse(module_ast)


def build() -> Any:
    source = _build_python()
    spec = spec_from_loader("tempered.components", loader=None)
    assert spec is not None
    module = module_from_spec(spec)
    exec(source, module.__dict__)
    sys.modules["tempered.components"] = module
    return module


def build_to(module: ModuleType):
    source = _build_python()
    source = autopep8.fix_code(source)
    if not module.__file__:
        raise ValueError("Module must be loaded from a file")

    with open(module.__file__, "w") as f:
        f.write(source)

    importlib.reload(module)


def build_static():
    try:
        components = _load_static_file()
    except Exception:
        BUILD_FILE.unlink(missing_ok=True)
        BUILD_FILE.touch()
        components = _load_static_file()

    build_to(components)
    return components


def _load_static_file():
    from tempered.generated import __components
    importlib.reload(__components)
    return __components
