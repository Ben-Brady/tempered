from tempered.parser import parse_template, TemplateParameter, RequiredParameter, LiteralBlock, IfBlock


def test_parse_if_block():
    template = parse_template("abc", """
        {% if True %}
            a
        {% else %}
            b
        {% endif %}
    """)
    block = template.body[0]
    assert isinstance(block, IfBlock)
    assert len(block.if_block) == 1 and isinstance(block.if_block[0], LiteralBlock)
    assert block.else_block and len(block.else_block) == 1 and isinstance(block.else_block[0], LiteralBlock)
