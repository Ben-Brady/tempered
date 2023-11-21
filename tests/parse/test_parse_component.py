from tempered.parser import parse_template, parse_ast
import ast


def test_parse_component_block():
    template = parse_template("abc",
        "{<Post(a=1)>}"
    )
    block = template.body[0]
    assert isinstance(block, parse_ast.ComponentBlock)
    assert "a" in block.keywords

