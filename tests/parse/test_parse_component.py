from tempered.parser import parse_template, template_ast


def test_parse_component_block():
    template = parse_template("abc", "{<Post(a=1)>}")
    block = template.body[0]
    assert isinstance(block, template_ast.ComponentNode)
    assert "a" in block.keywords
