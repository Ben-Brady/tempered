from . import build_template
from tempered.parser import Template, LiteralBlock


def test_template_add_styles():
    CSS = "a{color:red;}"
    func = build_template(Template(
        name="post",
        body=[
            LiteralBlock("Bar!"),
        ],
        style=CSS
    ))

    assert CSS in func(with_styles=True)


def test_template_wont_add_styles():
    CSS = "a{color:red;}"
    func = build_template(Template(
        name="post",
        body=[
            LiteralBlock("Bar!"),
        ],
        style=CSS
    ))

    assert CSS not in func(with_styles=False)
