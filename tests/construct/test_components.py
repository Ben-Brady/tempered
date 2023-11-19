from . import build_template
import tempered
from tempered import parser, ast_utils
import ast


def test_components_prevent_css_duplication():
    components = tempered.Tempered()
    child_template = parser.Template(
        name="child",
        parameters=[parser.TemplateParameter(name="value")],
        body=[
            parser.ExprBlock(value=ast.Name(id="value")),
        ],
        css="div { a: b}",
    )
    parent_template = parser.Template(
        name="parent",
        body=[
            parser.ComponentBlock(
                component_name="child",
                keywords={
                    "value": ast_utils.create_constant("a"),
                    "with_styles": ast_utils.create_constant(True),
                },
            ),
            parser.ComponentBlock(
                component_name="child",
                keywords={
                    "value": ast_utils.create_constant("a"),
                    "with_styles": ast_utils.create_constant(False),
                },
            ),
            parser.StyleBlock(),
        ],
        child_components=["child"],
    )

    components.add_template_obj(child_template)
    components.add_template_obj(parent_template)
    module = components.build_memory()
    html: str = module.parent(with_styles=True)
    assert html.count(child_template.css) == 1


def test_components_calculated_nested_children():
    CSS_KEY = "ASDF"
    components = tempered.Tempered()
    components.add_template_obj(
        parser.Template(
            name="a",
            body=[
                parser.StyleBlock()
            ],
            child_components=["b"],
        )
    )
    components.add_template_obj(
        parser.Template(
            name="b",
            child_components=["c", "d"],
        )
    )
    components.add_template_obj(
        parser.Template(
            name="c",
        )
    )
    components.add_template_obj(
        parser.Template(
            name="d",
            css=f"div {{ content: '{CSS_KEY}'; }} ",
            child_components=["b"],
        )
    )

    module = components.build_static()
    html = module.a(with_styles=True)
    assert CSS_KEY in html
