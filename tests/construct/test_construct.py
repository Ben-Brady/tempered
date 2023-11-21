from . import build_template
from tempered.parser import Template, TemplateParameter, parse_ast, tokens
import ast


def test_assemble_literals():
    func = build_template(Template(
        name="post",
        body=[
            parse_ast.LiteralBlock("Foo!"),
            parse_ast.LiteralBlock("Bar!"),
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
            parse_ast.ExprBlock(value=ast.Name(id="value")),
        ],
    ))

    assert func(value="example text") == "example text", "Parameters aren't used"

