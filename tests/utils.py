from functools import partial
import tempered
import typing_extensions as t
from typing_extensions import Callable


def build_template(template: str) -> Callable:
    env = tempered.Tempered()
    env.add_template_from_string("main", template)
    return partial(env.render_template, "main")


def build_templates(template: str, *other_templates: t.Tuple[str, str]) -> Callable:
    env = tempered.Tempered()

    templates = {name: body for (name, body) in other_templates}
    templates["main"] = template
    env.add_templates_from_string(templates)
    return partial(env.render_template, "main")
