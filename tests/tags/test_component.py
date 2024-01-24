from . import build_template, build_templates
import pytest
import tinycss2
import tempered


def test_components_can_have_optional_closing_tag():
    component = build_templates(
        """
            {<comp ()/>}
            {<comp ()>}
        """,
        (
            "comp",
            """
         test
        """,
        ),
    )

    html: str = component()
    assert html.count("test") == 2, html


def test_components_prevent_css_duplication():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        """
            {% import Child from "child" %}
            {<Child()>}
            {<Child()>}
        """,
        (
            "child",
            f"""
         <a>test</a>
         <style>
            a {{ color: {CSS_KEY}; }}
         </style>
        """,
        ),
    )
    html: str = component()
    assert html.count(CSS_KEY) == 1, html


def test_components_calculated_nested_children():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        '{% import A from "a" %} {<A()>}',
        ("a", '{% import B from "b" %} {<B()>}'),
        ("b", '{% import C from "c" %} {<C()>}'),
        ("c", '{% import D from "d" %} {<D()>}'),
        (
            "d",
            f"<style>a {{ color: {CSS_KEY}; }}</style>",
        ),
    )
    html = component()
    assert html.count(CSS_KEY) == 1, html
