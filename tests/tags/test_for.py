from utils import build_template
import pytest


def test_empty_for_loop():
    component = build_template(
        """
        {% for x in range(5) %}{% endfor %}
    """
    )
    component()


def test_for_range_loop():
    component = build_template(
        """
        {% for x in range(5) %}{{ x }}{% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html


def test_for_each_loop():
    component = build_template(
        """
        {% for item in items %}{{ item }}{% endfor %}
    """
    )
    items = ["a", "b", "c"]
    html = component(items=items)
    for item in items:
        assert item in html


def test_for_range_loop_with_unroll():
    component = build_template(
        """
        {% for x in range(5) %}
            {{ x }}
        {% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html
