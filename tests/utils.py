import tempered
from typing import Callable


def build_template(template) -> Callable:
    components = tempered.Tempered()
    components.add_template("foo", template)
    module = components.build_memory()
    return getattr(module, "foo")
