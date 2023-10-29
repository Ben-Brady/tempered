import tempered
from tempered.parser import Template
from typing import Callable


def build_template(template: Template) -> Callable:
    components = tempered.Tempered()
    components.add_template_obj(template)
    module = components.build_memory()
    return getattr(module, template.name)
