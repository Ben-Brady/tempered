from typing import Sequence
import typing_extensions as t
from ..css import finalise_css
from ..parser import Template


def generate_css(
    template: Template,
    lookup: t.Dict[str, Template],
) -> str:
    components_used = calculate_dependencies(template, lookup)
    css_fragments = [lookup[comp].css for comp in components_used]
    css = " ".join(css_fragments)
    css = finalise_css(css)
    return css


component_cache: t.Dict[str, t.Set[str]] = {}


def calculate_dependencies(
    template: Template,
    lookup: t.Dict[str, Template],
) -> Sequence[str]:
    dependencies = _recursively_calculate_dependencies(template, lookup)
    component_cache.clear()
    return dependencies


def _recursively_calculate_dependencies(
    template: Template,
    lookup: t.Dict[str, Template],
) -> Sequence[str]:
    if template.name in component_cache:
        return list(component_cache[template.name])

    components_used: t.Set[str] = set()
    components_used.add(template.name)

    required_names = [import_.name for import_ in list(template.imports)]
    if template.layout:
        required_names.append(template.layout)

    for name in list(required_names):
        child = lookup[name]
        child_children = calculate_dependencies(child, lookup)
        components_used.update(child_children)

    component_cache[template.name] = components_used
    return list(components_used)
