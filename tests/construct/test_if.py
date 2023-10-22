from . import build_template
from tempered.parser import Template, LiteralBlock, TemplateParameter, IfBlock
import ast


def test_if_block():
    template = Template(
        name="if_template",
        body=[IfBlock(
            condition=ast.Constant(value=True),
            if_block=[
                LiteralBlock("True")
            ],
            else_block=[
                LiteralBlock("False")
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
        body=[IfBlock(
            condition=ast.Name(id="block"),
            if_block=[
                LiteralBlock("A")
            ],
            else_block=[
                LiteralBlock("B")
            ]
        )],
    )
    func = build_template(template)
    assert func(block=True) == "A", "Expression isn't escaped"
    assert func(block=False) == "B", "Expression isn't escaped"

