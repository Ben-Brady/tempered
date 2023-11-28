from utils import build_template
import bs4
import pytest


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
