import tempered
from typing_extensions import Callable, LiteralString
import typing_extensions as t


def build_template(template: str) -> Callable:
    components = tempered.Tempered()
    components.add_template_from_string("foo", template)
    module = components.build_static()
    return getattr(module, "foo")


def build_templates(
    template: str, *other_templates: t.Tuple[str, str]
) -> Callable:
    components = tempered.Tempered()
    components.add_template_from_string("foo", template)
    for name, body in other_templates:
        components.add_template_from_string(name, body)
    module = components.build_static()
    return getattr(module, "foo")
