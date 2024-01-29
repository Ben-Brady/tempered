import typing_extensions as t
from . import ast_utils, parser
from .compiler.constants import REGISTER_GLOBAL_FUNC, template_func_name
from .compiler.module import compile_module


def build(
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
) -> t.Dict[str, t.Any]:
    module_ast = compile_module(templates)
    source = ast_utils.unparse(module_ast)

    module_globals = {}
    exec(source, module_globals)

    # Register globals
    for name, value in globals.items():
        module_globals[REGISTER_GLOBAL_FUNC](name, value)

    return module_globals


def build_single_template(
    template: parser.Template,
    templates: t.List[parser.Template],
    globals: t.Dict[str, t.Any],
) -> t.Callable[..., str]:
    module = build([template, *templates], globals)
    func_name = template_func_name(template.name, template.is_layout)
    template_func = module[func_name]
    return template_func
