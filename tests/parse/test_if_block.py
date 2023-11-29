from tempered.parser import parse_template, TemplateParameter, template_ast


def test_parse_if_block():
    template = parse_template("abc",
        "{% if True %}"
        "a"
        "{% else %}"
        "b"
        "{% endif %}"
    )
    block = template.body[0]
    assert isinstance(block, template_ast.IfTag)
    assert len(block.if_block) == 1
    assert isinstance(block.if_block[0], template_ast.LiteralTag)
    assert block.else_block and len(block.else_block) == 1 and isinstance(block.else_block[0], template_ast.LiteralTag)


def test_parse_if_block_with_condition():
    template = parse_template("abc",
        "{% if 2 > 3 %}"
            "a"
        "{% else %}"
            "b"
        "{% endif %}"
    )
    block = template.body[0]
    assert isinstance(block, template_ast.IfTag)
    assert len(block.if_block) == 1
    assert isinstance(block.if_block[0], template_ast.LiteralTag)
    assert block.else_block and len(block.else_block) == 1
    assert isinstance(block.else_block[0], template_ast.LiteralTag)
