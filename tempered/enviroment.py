from __future__ import annotations
from dataclasses import dataclass
import typing_extensions as t
from . import build, parser


@dataclass
class Template:
    _func: t.Callable[..., str]
    _parse_info: parser.Template

    def render(self, **context: t.Any) -> str:
        return self._func(**context)


class Environment:
    _templates: t.Dict[str, Template]
    _globals: t.Dict[str, Template]
    _from_string_cache: t.Dict[str, Template]

    def __init__(
        self,
        templates: t.Optional[t.Dict[str, Template]] = None,
        globals: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self._templates = templates or {}
        self._globals = globals or {}
        self._from_string_cache = {}

    def get_template(self, template_name: str) -> t.Optional[Template]:
        return self._templates.get(template_name, None)

    def render_template(self, template_name: str, **context: t.Any) -> str:
        template = self.get_template(template_name)
        if template is None:
            raise ValueError(f"Template '{template_name}' not found")

        return template.render(**context)

    def from_string(self, template: str) -> Template:
        if template in self._from_string_cache:
            return self._from_string_cache[template]

        parsed_template = parser.parse_template("<string>", template)
        templates = [template._parse_info for template in self._templates.values()]
        func = build.build_single_template(
            parsed_template,
            templates,
            self._globals,
        )
        template_obj = Template(
            _func=func,
            _parse_info=parsed_template,
        )
        self._from_string_cache[template] = template_obj
        return template_obj
