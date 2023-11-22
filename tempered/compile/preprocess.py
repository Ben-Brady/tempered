from .. import ast_utils
from ..parser import Template
from typing import Sequence



def calculate_required_css(
    template: Template,
    lookup: dict[str, Template]) -> str:
    components_used = _calculate_required_components(template, lookup)
    component_cache.clear()
    css_fragments = [
        lookup[comp].css
        for comp in components_used
    ]
    return " ".join(css_fragments)


component_cache: dict[str, set[str]] = {}
def _calculate_required_components(
    template: Template,
    lookup: dict[str, Template]
    )-> Sequence[str]:
    if template.name in component_cache:
        return list(component_cache[template.name])

    components_used: set[str] = set()
    components_used.add(template.name)

    for call in list(template.components_calls):
        child = lookup[call.component_name]
        child_children = _calculate_required_components(child, lookup)
        components_used.update(child_children)

    component_cache[template.name] = components_used
    return list(components_used)
