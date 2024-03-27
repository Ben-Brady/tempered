from tests import build_templates, test


@test("Components prevent css duplication")
def _():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        """
            {% import Child from "child" %}
            {% component Child() %}
            {% component Child() %}
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


@test("Components account for nested children")
def _():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        '{% import A from "a" %} {% component A() %}',
        ("a", '{% import B from "b" %} {% component B() %}'),
        ("b", '{% import C from "c" %} {% component C() %}'),
        ("c", '{% import D from "d" %} {% component D() %}'),
        (
            "d",
            f"<style>a {{ color: {CSS_KEY}; }}</style>",
        ),
    )
    html = component()
    assert html.count(CSS_KEY) == 1, html


@test("Components accept parameters")
def _():
    component = build_templates(
        """
        {% import Comp from "comp" %}
        {% component Comp(foo="bar") %}
        """,
        ("comp", "{% param foo: str %}{{foo}}"),
    )
    html = component()
    assert "bar" in html


@test("Components allow default parameters")
def _():
    component = build_templates(
        '{% import Comp from "comp" %}{% component Comp() %}',
        ("comp", '{% param foo: str = "bar" %}{{foo}}'),
    )
    html = component()
    assert "bar" in html


@test("Components allows mixed parameters")
def _():
    component = build_templates(
        """
            {% import Comp from "comp" %}
            {% component Comp(bar="bar") %}
        """,
        (
            "comp",
            """
            {% param foo: str = "foo" %}
            {% param bar: str %}
            {{foo}}-{{bar}}
            """,
        ),
    )
    html = component()
    assert "foo-bar" in html
