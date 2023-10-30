from . import build_template
from tempered import parser


def test_template_add_styles():
    CSS = "a{color:red;}"
    func = build_template(parser.Template(
        name="post",
        body=[
            parser.LiteralBlock("Bar!"),
            parser.StyleBlock(),
        ],
        css=CSS
    ))

    assert CSS in func(with_styles=True)


def test_template_wont_add_styles():
    CSS = "a{color:red;}"
    func = build_template(parser.Template(
        name="post",
        body=[
            parser.LiteralBlock("Bar!"),
            parser.StyleBlock(),
        ],
        css=CSS
    ))

    assert CSS not in func(with_styles=False)


def test_template_places_styles():
    CSS = "B"
    func = build_template(parser.Template(
        name="post",
        body=[
            parser.LiteralBlock("A"),
            parser.StyleBlock(),
            parser.LiteralBlock("C"),
        ],
        css=CSS
    ))

    assert func() == "A<style>B</style>C"
