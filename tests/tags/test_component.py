from . import build_templates


def test_components_can_have_optional_closing_tag():
    component = build_templates(
        """
        {% import Comp from "comp" %}
            {% component Comp() %}
            {% component Comp() %}
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


def test_components_calculated_nested_children():
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


def test_components_take_parameters():
    component = build_templates(
        """
        {% import Comp from "comp" %}
        {% component Comp(foo="bar") %}
        """,
        ("comp", "{% param foo: str %}{{foo}}"),
    )
    html = component()
    assert "bar" in html


def test_components_allows_default_parameters():
    component = build_templates(
        '{% import Comp from "comp" %}{% component Comp() %}',
        ("comp", '{% param foo: str = "bar" %}{{foo}}'),
    )
    html = component()
    assert "bar" in html


def test_components_allows_mixed_parameters():
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
