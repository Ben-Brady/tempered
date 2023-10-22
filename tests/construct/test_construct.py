from . import build_template
from tempered.parser import Template, LiteralBlock, TemplateParameter, ExprBlock, IfBlock
import ast


def test_assemble_literals():
    func = build_template(Template(
        name="post",
        body=[
            LiteralBlock("Foo!"),
            LiteralBlock("Bar!"),
        ],
    ))

    assert func() == "Foo!Bar!"


def test_use_parameters():
    func = build_template(Template(
        name="post",
        parameters=[
            TemplateParameter(name="value")
        ],
        body=[
            ExprBlock(value=ast.Name(id="value")),
        ],
    ))

    assert func(value="example text") == "example text", "Parameters aren't used"

