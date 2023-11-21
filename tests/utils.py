import tempered
from typing_extensions import Callable, LiteralString


def build_template(template: LiteralString) -> Callable:
    components = tempered.Tempered()
    components.add_template("foo", template)
    module = components.build_memory()
    return getattr(module, "foo")


def build_templates(
    template: LiteralString,
    *other_templates: tuple[str, LiteralString]
) -> Callable:
    components = tempered.Tempered()
    components.add_template("foo", template)
    for name, body in other_templates:
        components.add_template(name, body)
    module = components.build_memory()
    return getattr(module, "foo")
