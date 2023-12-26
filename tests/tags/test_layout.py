import utils
from tempered import Tempered
import bs4
import pytest


def test_layout_extend_with_default_slot():
    func = utils.build_templates(
        """
        {% layout "a" %}
        Test
        """,
        ("a", "<div>{% slot %}</div>"),
    )

    soup = bs4.BeautifulSoup(func(), "html.parser")

    tag = soup.find("div")
    assert tag and "Test" in tag.text  # type:ignore


def test_layout_migrates_css():
    CSS_KEY = "TEMPERED_CSS"

    func = utils.build_templates(
        f"""
        {{% layout "a" %}}
        Test
        <style>
        a {{ content: '{CSS_KEY}'; }}
        </style>
        """,
        ("a", "{%styles%} {% slot %}"),
    )
    html = func()
    soup = bs4.BeautifulSoup(html, "html.parser")

    assert soup.find("style")
    assert CSS_KEY in soup.find("style").text  # type:ignore


def test_layout_extend_with_named_slots():
    func = utils.build_templates(
        """
        {% layout "layout" %}
        {% block title %}Test{% endblock %}
        """,
        ("layout", "<title>{% slot title required %}</title>"),
    )
    soup = bs4.BeautifulSoup(func(), "html.parser")
    assert soup.find("title")
    assert "Test" in soup.find("title").text  # type:ignore


def test_layout_extend_with_many_named_slots():
    func = utils.build_templates(
        """
        {% layout "layout" %}
        {% block a %}A{% endblock %}
        {% block b %}B{% endblock %}
        """,
        (
            "layout",
            """
                <b>{% slot b required %}</b>
                <a>{% slot a required %}</a>
                """,
        ),
    )
    soup = bs4.BeautifulSoup(func(), "html.parser")
    assert "A" in soup.find("a").text  # type:ignore
    assert "B" in soup.find("b").text  # type:ignore


def test_layout_respects_with_styles():
    CSS_KEY = "TEMPERED"
    func = utils.build_templates(
        """
        {% layout "layout" %}
        """,
        (
            "layout",
            f"""
                {{% styles %}}
                {{% slot %}}
                <style>
                    a {{ content: '{CSS_KEY}'; }}
                </style>
            """,
        ),
    )
    html = func(with_styles=True)
    assert CSS_KEY in func(with_styles=True)
    assert CSS_KEY not in func(with_styles=False)


def test_layout_styles_are_combined():
    CSS_LAYOUT = "TEMPERED_LAYOUT"
    CSS_COMP = "TEMPERED_COMP"
    component = f"""
        {{% layout "layout" %}}
        <style>
            a {{content: '{CSS_COMP}'; }}
        </style>
    """
    layout = f"""
        {{% styles %}}
        {{% slot %}}
        <style>
            a {{ content: '{CSS_LAYOUT}'; }}
        </style>
    """

    func = utils.build_templates(
        component,
        ("layout", layout),
    )
    styled_html = func(with_styles=True)
    assert CSS_LAYOUT in styled_html, "Doesn't contain layout css"
    assert CSS_COMP in styled_html, "Doesn't contain component css"
