from ..errors import InvalidTemplate
from ..parser.template_ast import Template, LayoutTemplate
from .preprocess import calculate_dependencies
import typing_extensions as t


def validate_templates(templates: t.Sequence[Template]):
    template_lookup = {template.name: template for template in templates}
    for template in templates:
        _check_for_missing_layout(template, template_lookup)
        _check_for_missing_blocks(template, template_lookup)
        _check_for_non_existant_blocks(template, template_lookup)


def _check_for_missing_layout(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    if template.layout not in lookup:
        raise InvalidTemplate.create(
            msg=f"Missing layout '{template.layout}'",
            name=template.name,
            file=template.file,
        )

    if not isinstance(lookup[template.layout], LayoutTemplate):
        raise InvalidTemplate.create(
            msg=f"'{template.layout}' is not a layout",
            name=template.name,
            file=template.file,
        )


def _check_for_missing_blocks(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    layout = t.cast(LayoutTemplate, lookup[template.layout])
    for slot in layout.slots:
        slot_used = slot.name in template.blocks
        if slot.is_required and not slot_used:
            raise InvalidTemplate.create(
                msg=f"'{template.layout}' requires slot '{slot.name}'",
                name=template.name,
                file=template.file,
            )


def _check_for_non_existant_blocks(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    layout = t.cast(LayoutTemplate, lookup[template.layout])
    slot_names = [slot.name for slot in layout.slots]
    for block in template.blocks:
        if block not in slot_names:
            raise InvalidTemplate.create(
                msg=f"'{template.layout}' doesn't have slot '{block}'",
                name=template.name,
                file=template.file,
            )

