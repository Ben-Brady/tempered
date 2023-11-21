from utils import build_template
import pytest
import tinycss2
import tempered


def test_single_constant_assignment():
    component = build_template("""
        {% set a = "abc" %}
        {{a}}
    """)

    assert "abc" in component()


def test_assignment_with_if():
    component = build_template("""
        {% set x = 1 %}
        {% if x % 2 == 0%}
            {% set type = "even" %}
        {% else %}
            {% set type = "odd" %}
        {% endif %}

        {{x}} is {{type}}
    """)

    assert "1 is odd" in component()
