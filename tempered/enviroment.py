import typing_extensions as t
from dataclasses import dataclass


@dataclass
class Template:
    _func: t.Callable[..., str]
    _globals: t.Dict[str, t.Any]

    def render(self, **context: t.Any) -> str:
        return self._func(**context)


class Environment:
    _templates: t.Dict[str, Template] = {}
    _globals: t.Dict[str, Template] = {}

    def __init__(self, templates: t.Dict[str, Template], globals: t.Dict[str, t.Any]):
        self._templates = templates
        self._globals = globals

    def get_template(self, name: str) -> t.Optional[Template]:
        return self._templates.get(name, None)

    def from_string(self, template: str) -> Template:
        raise NotImplementedError("from_string is not implemented yet")
