from tests import build_template


def test_if_block():
    component = build_template(
        """
        {% if True %}
            True
        {% else %}
            False
        {% endif %}
    """
    )
    assert "True" in component()


def test_if_block_is_dynamic():
    component = build_template(
        """
        {% if expr %}
            True
        {% else %}
            False
        {% endif %}
    """
    )
    assert "True" in component(expr=True) and "False" not in component(expr=True)
    assert "False" in component(expr=False) and "True" not in component(expr=False)


def test_elif_block():
    component = build_template(
        """
        {% if expr_a %}
            a
        {% elif expr_b %}
            b
        {% endif %}
    """
    )
    assert "a" in component(expr_a=True, expr_b=True)
    assert "a" in component(expr_a=True, expr_b=False)
    assert "b" in component(expr_a=False, expr_b=True)


def test_empty_if_block():
    component = build_template("{% if True %}{% endif %}")
    assert component() == ""


def test_empty_if_blocks():
    component = build_template("{% if True %}{% elif True %}{% else %}{% endif %}")
    assert component() == ""
