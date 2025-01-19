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
    assert "True" in component(expr=True)
    assert "False" not in component(expr=True)
    assert "False" in component(expr=False)
    assert "True" not in component(expr=False)


def test_elif_block():
    component = build_template(
        """
        <t:if condition="expr_a">
            a
        </t:if>
        <t:elif condition="expr_b">
            b
        </t:elif>
    """
    )
    assert "a" in component(expr_a=True, expr_b=True)
    assert "a" in component(expr_a=True, expr_b=False)
    assert "b" in component(expr_a=False, expr_b=True)

def test_elif_and_else_block():
    component = build_template(
        """
        <ul>

        <t:if condition="a">
            a
        </t:if>
        <t:elif condition="b">
            b
        </t:elif>
        <t:else>
            c
        </t:else>
        </ul>
    """
    )
    assert "a" in component(a=True, b=True)
    assert "a" in component(a=True, b=False)
    assert "b" in component(a=False, b=True)
    assert "c" in component(a=False, b=False)


def test_multiple_elif_and_else_block():
    component = build_template(
        """
        <t:if condition="a">
            a
        </t:if>
        <t:elif condition="b">
            b
        </t:elif>
        <t:elif condition="c">
            c
        </t:elif>
        <t:else>
            d
        </t:else>
    """
    )
    assert "a" in component(a=True, b=True, c=True)
    assert "a" in component(a=True, b=True, c=False)
    assert "a" in component(a=True, b=False, c=True)
    assert "a" in component(a=True, b=False, c=False)

    assert "b" in component(a=False, b=True, c=False)
    assert "b" in component(a=False, b=True, c=True)

    assert "c" in component(a=False, b=False, c=True)
    assert "d" in component(a=False, b=False, c=False)


def test_empty_if_block():
    component = build_template('<t:if condition="True"></t:if>')
    assert component() == ""


def test_empty_if_blocks():
    component = build_template("""<t:if condition="True"></t:if><t:else></t:else>""")
    assert component() == ""
