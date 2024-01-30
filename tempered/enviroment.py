from __future__ import annotations
from dataclasses import dataclass
from types import ModuleType
import typing_extensions as t
from . import build, parser


@dataclass
class Template:
    _func: t.Callable[..., str]
    _parse_info: parser.Template

    def render(self, **context: t.Any) -> str:
        return self._func(**context)


class Environment:
    _from_string_cache: t.Dict[str, Template]
    _templates: t.Dict[str, Template]
    _module: ModuleType

    def __init__(self, module: t.Optional[ModuleType] = None):
        self._from_string_cache = {}
        if module is None:
            module = build.build_intial_module()

        self._module = module
        templates = build.get_templates(module)

        self._templates = {}
        for template in templates:
            template_func = build.get_template_func(module, template)
            self._templates[template.name] = Template(template_func, template)

    def get_template(self, template_name: str) -> t.Optional[Template]:
        return self._templates.get(template_name, None)

    def render_template(self, template_name: str, **context: t.Any) -> str:
        template = self.get_template(template_name)
        if template is None:
            raise ValueError(f"Template '{template_name}' not found")

        return template.render(**context)

    def from_string(self, template: str) -> Template:
        """
        - TODO: Build without linkage, so it doesn't mutate the module
        """
        if template in self._from_string_cache:
            return self._from_string_cache[template]

        parsed_template = parser.parse_template("<string>", template)
        build.build_templates(self._module, [parsed_template])

        func = build.get_template_func(self._module, parsed_template)
        template_obj = Template(func, parsed_template)

        self._from_string_cache[template] = template_obj
        return template_obj
