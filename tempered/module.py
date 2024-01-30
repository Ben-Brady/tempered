from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType
import typing_extensions as t
from . import compiler, parser
from .compiler import constants


class TemperedModule:
    module: ModuleType

    def __init__(self):
        spec = spec_from_loader(name="tempered.generated", loader=None)
        if spec is None:
            raise RuntimeError("InteralError: Failed to create module spec")

        module = module_from_spec(spec)

        source = compiler.default_module_code()
        exec(source, module.__dict__)
        self.module = module

    def register_global(self, name: str, value: t.Any):
        register_global = self.module.__dict__[constants.REGISTER_GLOBAL_FUNC]
        register_global(name, value)

    def get_templates(self) -> t.List[parser.Template]:
        return self.module.__dict__[constants.TEMPLATE_LIST_VAR]

    def get_template_func(self, name: str) -> t.Callable[..., str]:
        name_lookup = self.module.__dict__[constants.NAME_LOOKUP_VAR]
        return name_lookup[name]

    def build_templates(self, templates: t.List[parser.Template]):
        existing_templates = self.get_templates()
        source = compiler.create_template_functions_code(templates, existing_templates)
        exec(source, self.module.__dict__)

        register_template = self.module.__dict__[constants.REGISTER_TEMPLATE_FUNC]
        for template in templates:
            register_template(template)
