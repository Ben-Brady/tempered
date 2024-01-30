from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType
import typing_extensions as t
from . import ast_utils, compiler, parser
from .compiler import constants


def build_intial_module() -> ModuleType:
    source = compiler.create_default_module_code()

    spec = spec_from_loader(name="tempered.generated", loader=None)
    if spec is None:
        raise RuntimeError("InteralError: Failed to create module spec")

    module = module_from_spec(spec)
    exec(source, module.__dict__)

    return module


def build_templates(
    module: ModuleType,
    templates: t.List[parser.Template],
):
    source = compiler.create_add_templates_code(templates, module)
    exec(source, module.__dict__)


def register_global(
    module: ModuleType,
    name: str,
    value: t.Any,
):
    register_global = module.__dict__[constants.REGISTER_GLOBAL_FUNC]
    register_global(name, value)


def get_templates(module: ModuleType) -> t.List[parser.Template]:
    return module.__dict__[constants.TEMPLATE_LIST_VAR]


def get_template_func(module: ModuleType, name: str) -> t.Callable[..., str]:
    lookup = module.__dict__[constants.NAME_LOOKUP_VAR]
    return lookup[name]
