from tempered.compile import compile_module
from tempered.main import _build_python, _templates, build
from tempered.parser import Template
import ast
from typing import Callable


def build_template(template: Template) -> Callable:
    _templates.append(template)
    module = build()
    return getattr(module, template.name)
