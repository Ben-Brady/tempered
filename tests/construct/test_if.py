from . import build_template
from tempered.parser import Template, parse_ast, TemplateParameter
import ast


def test_if_block():
    template = Template(
        name="if_template",
        body=[parse_ast.IfBlock(
            condition=ast.Constant(value=True),
            if_block=[
                parse_ast.LiteralBlock("True")
            ],
            else_block=[
                parse_ast.LiteralBlock("False")
            ]
        )],
    )
    func = build_template(template)
    assert func() == "True", "Expression isn't escaped"


def test_if_block_is_dynamic():
    template = Template(
        name="if_template",
        parameters=[
            TemplateParameter(name="block")
        ],
        body=[parse_ast.IfBlock(
            condition=ast.Name(id="block"),
            if_block=[
                parse_ast.LiteralBlock("A")
            ],
            else_block=[
                parse_ast.LiteralBlock("B")
            ]
        )],
    )
    func = build_template(template)
    assert func(block=True) == "A", "Expression isn't escaped"
    assert func(block=False) == "B", "Expression isn't escaped"

