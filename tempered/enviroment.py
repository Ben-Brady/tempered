from . import build, parser
import typing_extensions as t
from dataclasses import dataclass


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

    def __init__(self, templates: t.Dict[str, Template], globals: t.Dict[str, t.Any]):
        self._templates = templates
        self._globals = globals
        self._from_string_cache = {}

    def get_template(self, name: str) -> t.Optional[Template]:
        return self._templates.get(name, None)

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
