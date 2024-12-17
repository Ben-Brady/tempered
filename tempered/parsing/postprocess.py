from . import nodes
from ..introspection.introspecter import TemplateInfo
from .nodes import TemplateBlock


def postprocess(body: TemplateBlock, info: TemplateInfo, css: str) -> TemplateBlock:
    body = place_default_style_node(body, info, css)
    return body


def place_default_style_node(
    body: TemplateBlock, info: TemplateInfo, css: str
) -> TemplateBlock:
    if info.styles_set:
        return body

    has_css = any((
        len(css) != 0,
        len(info.style_includes) != 0,
        len(info.components_calls) != 0
    ))

    # If there is no CSS and it's not a layout
    # If there can never be additional css
    # So don't place a style tag
    if not info.is_layout and not has_css:
        return body

    return [*body, nodes.StyleNode()]