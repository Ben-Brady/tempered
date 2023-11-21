from .. import ast_utils
from ..parser import Template
from typing import Sequence

def update_template_nested_children(templates: Sequence[Template]):
    lookup = {template.name: template for template in templates}
    checked = set()

    def update(template: Template):
        if template.name in checked:
            return

        checked.add(template.name)
        for child_name in list(template.child_components):
            child = lookup[child_name]
            update(child)
            template.child_components.update(child.child_components)

    for template in templates:
        update(template)
