from . import build_template
import tempered
from tempered import parser, ast_utils
import ast


def test_components_prevent_css_duplication():
    components = tempered.Tempered()
    child_template = parser.Template(
        name="child",
        parameters=[
            parser.TemplateParameter(name="value")
        ],
        body=[
            parser.ExprBlock(value=ast.Name(id="value")),
        ],
        css="div { a: b}",
    )
    child_call = ast_utils.create_call(
        func=ast_utils.create_name("child"),
        args=[],
        keywords={
            "value": ast_utils.create_constant("a"),
            "with_styles": ast_utils.create_constant(True),
        }
    )
    parent_template = parser.Template(
        name="parent",
        body=[
            parser.ComponentBlock(
                component_name="child",
                component_call=child_call,
            ),
            parser.ComponentBlock(
                component_name="child",
                component_call=child_call,
            ),
        ],
        child_components=["child"],
    )

    components.add_template_obj(child_template)
    components.add_template_obj(parent_template)
    module = components.build_memory()
    html: str = module.parent()
    assert html.count(child_template.css) == 1

