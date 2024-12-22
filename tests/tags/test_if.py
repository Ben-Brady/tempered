from tests import build_template


def test_if_block():
    component = build_template(
        """
        <t:if condition="True">
            True
        </t:if>
        <t:else>
            False
        </t:else>
    """
    )
    assert "True" in component()
    assert "False" not in component()


def test_if_block_is_dynamic():
    component = build_template(
        """
        <t:if condition="expr">
            True
        </t:if>
        <t:else>
            False
        </t:else>
    """
    )
    assert "True" in component(expr=True) and "False" not in component(expr=True)
    assert "False" in component(expr=False) and "True" not in component(expr=False)


def test_elif_block():
    component = build_template("""
        <t:if condition="expr_a">
            True
        </t:if>
        <t:elif condition="expr_b">
            False
        </t:elif>
    """)
    assert "a" in component(expr_a=True, expr_b=True)
    assert "a" in component(expr_a=True, expr_b=False)
    assert "b" in component(expr_a=False, expr_b=True)


def test_empty_if_block():
    component = build_template('<t:if condition="expr_a"></t:if>')
    assert component() == ""


def test_empty_if_blocks():
    component = build_template("""<t:if condition="True"></t:if><t:else></t:else>""")
    assert component() == ""
