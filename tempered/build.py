import typing_extensions as t
from . import ast_utils, parser, compiler
from .compiler import constants
from types import ModuleType
from importlib.util import module_from_spec, spec_from_loader


def build_intial_module() -> ModuleType:
    source = compiler.create_default_module_code()

    spec = spec_from_loader(name="tempered.generated", loader=None)
    if spec is None:
        raise RuntimeError("InteralError: Failed to create module spec")

    module = module_from_spec(spec)
    exec(source, module.__dict__)

    # Register globals

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


def get_template_func(
    module: ModuleType, template: parser.Template
) -> t.Callable[..., str]:
    func_name = constants.template_func_name(template.name, template.is_layout)
    template_func = module.__dict__[func_name]
    return template_func
