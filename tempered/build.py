from . import parser
from .compile.module import compile_module
import ast
import inspect
import importlib
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from types import ModuleType
import autopep8  # type: ignore


BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


def _build_python(
        templates: list[parser.Template],
        ) -> str:
    module_ast = compile_module(
        templates=templates,
    )
    return ast.unparse(module_ast)


def build_memory(
        templates: list[parser.Template],
        ) -> ModuleType:
    source = _build_python(templates)
    spec = spec_from_loader(name="tempered.components", loader=None)
    assert spec is not None
    module = module_from_spec(spec)
    exec(source, module.__dict__)
    return module


def build_to(
        module: ModuleType,
        templates: list[parser.Template],
        ):
    source = _build_python(templates)
    source = autopep8.fix_code(source)
    if not hasattr(module, "__file__") or module.__file__ is None:
        raise ValueError("Module must be loaded from a file")

    with open(module.__file__, "w") as f:
        f.write(source)

    importlib.reload(module)


def build_static(
        templates: list[parser.Template],
        ):
    try:
        components = _load_static_file()
    except Exception:
        BUILD_FILE.unlink(missing_ok=True)
        BUILD_FILE.touch()
        components = _load_static_file()

    build_to(components, templates)
    return components


def _load_static_file():
    from tempered.generated import _components
    importlib.reload(_components)
    return _components

