from ..errors import InvalidTemplate
from ..parser import parse_ast
from ..parser.parse_ast import Template
from typing_extensions import Sequence


def validate_templates(templates: Sequence[Template]):
    template_lookup = {
        template.name: template
        for template in templates
    }
    for template in templates:
        _check_for_missing_layout(template, template_lookup)
        _check_for_missing_blocks(template, template_lookup)
        _check_for_non_existant_blocks(template, template_lookup)
        _check_for_invalid_component_calls(template, template_lookup)


def _check_for_missing_layout(template: Template, lookup: dict[str, Template]):
    if template.layout is None:
        return

    if template.layout not in lookup:
        raise InvalidTemplate.create(
            msg=f"Missing layout '{template.layout}'",
            name=template.name,
            file=template.file,
        )


def _check_for_missing_blocks(template: Template, lookup: dict[str, Template]):
    pass


def _check_for_non_existant_blocks(template: Template, lookup: dict[str, Template]):
    pass


def _check_for_invalid_component_calls(template: Template, lookup: dict[str, Template]):
    for call in template.components_calls:
        if call.component_name not in lookup:
            raise InvalidTemplate.create(
                msg=f"Missing component '{call.component_name}'",
                file=template.file,
                name=template.name,
            )

        component = lookup[call.component_name]
        required_parameters = [
            param.name
            for param in component.parameters
            if param.default is None
        ]
        for param in required_parameters:
            if param not in call.keywords:
                raise InvalidTemplate.create(
                    msg=f"Missing required parameter '{param}' for component '{call.component_name}'",
                    file=template.file,
                    name=template.name,
                )

