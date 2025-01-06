import typing_extensions as t
from ..css.postprocess import postprocess_css
from ..parsing import Template
from .dependencies import calculate_dependencies


def generate_template_css(
    template: Template,
    lookup: t.Dict[str, Template],
) -> str:
    components_used = calculate_dependencies(template, lookup)
    css_fragments = [lookup[comp].css for comp in components_used]
    css = " ".join(css_fragments)
    css = postprocess_css(css)
    return css
