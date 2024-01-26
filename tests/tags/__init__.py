import tempered
import typing_extensions as t
from typing_extensions import Callable


def build_template(template: str) -> Callable:
    env = tempered.Environment()
    return env.from_string(template).render


def build_templates(template: str, *other_templates: t.Tuple[str, str]) -> Callable:
    components = tempered.Tempered()
    for name, body in other_templates:
        components.add_template_from_string(name, body)

    env = components.build_enviroment(generate_types=False)
    return env.from_string(template).render
