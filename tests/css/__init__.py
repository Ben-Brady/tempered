import tempered
from typing_extensions import Callable, LiteralString
import typing_extensions as t


def build_template(template: LiteralString) -> Callable:
    components = tempered.Tempered()
    components.add_template_from_string("foo", template)
    module = components.build_memory()
    return getattr(module, "foo")


def build_templates(
    template: LiteralString, *other_templates: t.Tuple[str, LiteralString]
) -> Callable:
    components = tempered.Tempered()
    components.add_template_from_string("foo", template)
    for name, body in other_templates:
        components.add_template_from_string(name, body)
    module = components.build_static()
    return getattr(module, "foo")
