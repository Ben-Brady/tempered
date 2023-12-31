from . import parser, ast_utils
from .compiler.module import compile_module
import sys
import importlib
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from types import ModuleType
import typing_extensions as t

BUILD_FILE = Path(__file__).parent.joinpath("generated/_components.py")


def _build_python(
    templates: t.List[parser.Template],
) -> str:
    module_ast = compile_module(templates=templates)
    return ast_utils.unparse(module_ast)


def build_memory(
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
) -> ModuleType:
    source = _build_python(templates)
    spec = spec_from_loader(name="tempered.components", loader=None)
    assert spec is not None
    module = module_from_spec(spec)
    exec(source, module.__dict__)
    _register_globals(module, globals)
    return module


def build_to(
    module: ModuleType,
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
):
    source = _build_python(templates)
    if not hasattr(module, "__file__") or module.__file__ is None:
        raise ValueError("Module must be loaded from a file")

    with open(module.__file__, "w") as f:
        f.write(source)

    module = importlib.reload(module)
    _register_globals(module, globals)
    return module


def build_static(
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
):
    try:
        components = _load_static_file()
    except Exception:
        sys.modules.pop("tempered.generated")
        if BUILD_FILE.exists():
            BUILD_FILE.unlink()

        BUILD_FILE.touch()
        components = _load_static_file()

    return build_to(
        components,
        templates,
        globals,
    )


def _load_static_file():
    importlib.invalidate_caches()
    from tempered.generated import _components

    importlib.reload(_components)
    return _components


def _register_globals(
    module: ModuleType,
    globals: t.Dict[str, t.Any],
):
    for name, value in globals.items():
        module.reigster_global(name, value)
