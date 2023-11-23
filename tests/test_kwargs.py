from utils import build_template, build_templates
import bs4
import pytest


def test_variables_are_converted_to_kwargs():
    func = build_template(
        """
        {% param a: int %}
        {{ a }}
        {{ b }}
    """
    )
    html = func(a="TEMPERED_A", b="TEMPERED_B")
    assert "TEMPERED_A" in html
    assert "TEMPERED_B" in html


def test_kwargs_passed_to_layout():
    func = build_templates(
        """
        {% layout "layout" %}
        """,
        ("layout", """
         {% slot %}
         {{ foo }}
         """),
    )

    assert "TEMPERED" in func(foo="TEMPERED")
