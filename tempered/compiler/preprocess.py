from ..parser import Template
from typing import Sequence
import typing_extensions as t


def calculate_required_css(
    template: Template,
    lookup: t.Dict[str, Template],
) -> str:
    components_used = calculate_dependencies(template, lookup)
    component_cache.clear()
    css_fragments = [lookup[comp].css for comp in components_used]
    return " ".join(css_fragments)


component_cache: t.Dict[str, t.Set[str]] = {}


def calculate_dependencies(
    template: Template,
    lookup: t.Dict[str, Template],
) -> Sequence[str]:
    if template.name in component_cache:
        return list(component_cache[template.name])

    components_used: t.Set[str] = set()
    components_used.add(template.name)

    required_names = [call.component_name for call in list(template.components_calls)]
    if template.layout:
        required_names.append(template.layout)

    for name in list(required_names):
        child = lookup[name]
        child_children = calculate_dependencies(child, lookup)
        components_used.update(child_children)

    component_cache[template.name] = components_used
    return list(components_used)
