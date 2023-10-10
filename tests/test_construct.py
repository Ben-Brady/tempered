from templater.construct import create_template_function
from templater.template import BlockLiteral, Template
import ast


def test_assemble_literals():
    func_ast = create_template_function(Template(
        name="post",
        body=[
            BlockLiteral("Foo!"),
            BlockLiteral("Bar!"),
        ],
        parameters=[],
        context={},
    ))
    func = ast.literal_eval(func_ast)
    assert func() == "Foo!Bar!"
