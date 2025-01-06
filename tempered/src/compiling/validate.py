import typing_extensions as t
from ..errors import InvalidTemplateException
from ..parsing.nodes import LayoutTemplate, Template


def validate_templates(templates: t.Sequence[Template]):
    template_lookup = {template.name: template for template in templates}
    for template in templates:
        check_for_invalid_imports(template, template_lookup)
        check_for_missing_component_import(template, template_lookup)
        check_for_missing_layout(template, template_lookup)
        check_for_missing_blocks(template, template_lookup)
        check_for_non_existant_blocks(template, template_lookup)
        check_for_duplicate_parameters(template)


def check_for_invalid_imports(template: Template, lookup: t.Dict[str, Template]):
    for _import in template.imports:
        import_name = _import.name
        if import_name not in lookup:
            raise InvalidTemplateException.create(
                msg=f"Imported component {import_name} could not be found",
                name=template.name,
                file=template.file,
            )


def check_for_missing_component_import(
    template: Template, lookup: t.Dict[str, Template]
):
    import_names = [x.target for x in template.imports]

    for call in template.components_calls:
        name = call.component_name
        if name not in import_names:
            raise InvalidTemplateException.create(
                msg=f"Component <t:{name} not imported",
                name=template.name,
                file=template.file,
            )


def check_for_missing_layout(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    if template.layout not in lookup:
        raise InvalidTemplateException.create(
            msg=f"Missing layout '{template.layout}'",
            name=template.name,
            file=template.file,
        )

    if not isinstance(lookup[template.layout], LayoutTemplate):
        raise InvalidTemplateException.create(
            msg=f"'{template.layout}' is not a layout",
            name=template.name,
            file=template.file,
        )


def check_for_missing_blocks(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    layout = t.cast(LayoutTemplate, lookup[template.layout])
    for slot in layout.slots:
        if slot.name == None:
            continue

        slot_used = slot.name in template.blocks
        if slot.is_required and not slot_used:
            raise InvalidTemplateException.create(
                msg=f"'{template.layout}' requires slot '{slot.name}'",
                name=template.name,
                file=template.file,
            )


def check_for_non_existant_blocks(template: Template, lookup: t.Dict[str, Template]):
    if template.layout is None:
        return

    layout = t.cast(LayoutTemplate, lookup[template.layout])
    slot_names = [slot.name for slot in layout.slots]
    for block in template.blocks:
        if block not in slot_names:
            raise InvalidTemplateException.create(
                msg=f"'{template.layout}' doesn't have slot '{block}'",
                name=template.name,
                file=template.file,
            )


def check_for_duplicate_parameters(template: Template):
    names = [param.name for param in template.parameters]
    if len(names) != len(set(names)):
        raise InvalidTemplateException.create(
            msg="Duplicate parameter names",
            name=template.name,
            file=template.file,
        )
