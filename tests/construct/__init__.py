from tempered.compile import compile_module
from tempered.parser import Template
import ast
from typing import Callable


def build_template(template: Template) -> Callable:
    module_ast = compile_module(templates=[template], type_imports=[])

    variables = globals()
    exec(ast.unparse(module_ast), variables)
    return variables[template.name]
