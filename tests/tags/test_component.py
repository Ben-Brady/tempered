from utils import build_template, build_templates
import pytest
import tinycss2
import tempered


def test_components_can_have_optional_closing_tag():
    component = build_templates(
        """
            {<comp ()/>}
            {<comp ()>}
        """,
        ("comp", """
         test
        """)
    )

    html: str = component()
    assert html.count("test") == 2, html


def test_components_prevent_css_duplication():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        """
            {<child()>}
            {<child()>}
        """,
        ("child", f"""
         <a>test</a>
         <style>
            a {{ color: {CSS_KEY}; }}
         </style>
        """)
    )
    html: str = component()
    assert html.count(CSS_KEY) == 1, html


def test_components_calculated_nested_children():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        "{<a()>}",
        ("a", "{<b()>}"),
        ("b", "{<c()>}"),
        ("c", "{<d()>}"),
        ("d", f"""
         <style>
            a {{ color: {CSS_KEY}; }}
         </style>
        """),
    )
    html = component()
    assert html.count(CSS_KEY) == 1, html

