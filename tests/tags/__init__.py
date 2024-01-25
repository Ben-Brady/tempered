import tempered
from typing_extensions import Callable
import typing_extensions as t


def build_template(template: str) -> Callable:
    env = tempered.Environment()
    return env.from_string(template).render


def build_templates(template: str, *other_templates: t.Tuple[str, str]) -> Callable:
    components = tempered.Tempered()
    for name, body in other_templates:
        components.add_template_from_string(name, body)

    env = components.build_enviroment()
    return env.from_string(template).render
