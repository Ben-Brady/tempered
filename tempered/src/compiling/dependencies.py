import typing_extensions as t
from ..parsing import Template


def calculate_dependencies(
    template: Template,
    lookup: t.Dict[str, Template],
) -> t.Sequence[str]:
    dependencies = _recursively_calculate_dependencies(template, lookup, {})
    return dependencies


def _recursively_calculate_dependencies(
    template: Template, lookup: t.Dict[str, Template], cache: t.Dict[str, t.Set[str]]
) -> t.Sequence[str]:
    if template.name in cache:
        return list(cache[template.name])

    components_used: t.Set[str] = set()
    components_used.add(template.name)

    required_names = [import_.name for import_ in list(template.imports)]
    if template.layout:
        required_names.append(template.layout)

    for name in list(required_names):
        child = lookup[name]
        child_children = _recursively_calculate_dependencies(child, lookup, cache)
        components_used.update(child_children)

    cache[template.name] = components_used
    return list(components_used)
