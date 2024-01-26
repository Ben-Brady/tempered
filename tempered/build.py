from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType
import typing_extensions as t
from . import ast_utils, parser
from .compiler.constants import component_func_name
from .compiler.module import compile_module


def build_memory(
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
) -> ModuleType:
    module_ast = compile_module(templates)

    source = ast_utils.unparse(module_ast)

    spec = spec_from_loader(name="tempered.components", loader=None)
    assert spec is not None
    module = module_from_spec(spec)
    exec(source, module.__dict__)

    # Register globals
    for name, value in globals.items():
        module.__register_global(name, value)

    return module


def build_single_template(
    template: parser.Template,
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
) -> t.Callable[..., str]:
    module = build_memory([template, *templates], globals)
    func = getattr(module, component_func_name(template.name))
    return func
