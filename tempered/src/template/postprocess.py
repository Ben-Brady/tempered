from ..parsing import nodes
from ..parsing.nodes import TemplateBlock
from .introspection import TemplateInfo


def place_default_style_node(
    body: TemplateBlock, info: TemplateInfo, css: str
) -> TemplateBlock:
    if info.styles_set:
        return body

    has_css = any(
        (len(css) != 0, len(info.style_includes) != 0, len(info.components_calls) != 0)
    )

    # If there is no CSS and it's not a layout
    # If there can never be additional css
    # So don't place a style tag
    if not info.is_layout and not has_css:
        return body

    return [*body, nodes.StyleNode()]
