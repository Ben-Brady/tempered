import typing_extensions as t
from . import template_ast
from .introspection import TemplateInfo
from .template_ast import Node, TemplateBlock


def postprocess(body: TemplateBlock, css: str, info: TemplateInfo) -> TemplateBlock:
    body = place_styles(body, css, info)
    return body


def place_styles(body: TemplateBlock, css: str, info: TemplateInfo) -> TemplateBlock:
    has_css_includes = len(info.style_includes) > 0 or len(info.components_calls) > 0
    has_css = len(css) > 0 or has_css_includes

    if info.styles_set:
        return body

    if not info.is_layout and not has_css:
        # If there is no CSS and it's not a layout
        # If there can never be additional css
        # So don't place a style tag
        return body

    return [*body, template_ast.StyleNode()]
