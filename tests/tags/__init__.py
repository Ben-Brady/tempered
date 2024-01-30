import tempered
import typing_extensions as t
from typing_extensions import Callable


def build_template(template: str) -> Callable:
    env = tempered.Environment()
    return env.from_string(template).render


def build_templates(template: str, *other_templates: t.Tuple[str, str]) -> Callable:
    components = tempered.Tempered()

    templates = {}
    templates["main"] = template
    for name, body in other_templates:
        templates[name] = body

    components.add_templates_from_string(templates)
    env = components.build_enviroment(generate_types=False)
    return env.from_string(template).render
