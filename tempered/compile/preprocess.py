from ..parser import Template
from typing import Sequence
import typing_extensions as t

def calculate_required_css(
    template: Template,
    lookup: t.Dict[str, Template]) -> str:
    components_used = _calculate_required_components(template, lookup)
    component_cache.clear()
    css_fragments = [
        lookup[comp].css
        for comp in components_used
    ]
    return " ".join(css_fragments)


component_cache: t.Dict[str, t.Set[str]] = {}
def _calculate_required_components(
    template: Template,
    lookup: t.Dict[str, Template]
    )-> Sequence[str]:
    if template.name in component_cache:
        return list(component_cache[template.name])

    components_used: t.Set[str] = set()
    components_used.add(template.name)

    for call in list(template.components_calls):
        child = lookup[call.component_name]
        child_children = _calculate_required_components(child, lookup)
        components_used.update(child_children)

    component_cache[template.name] = components_used
    return list(components_used)
