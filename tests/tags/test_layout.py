from tempered import Tempered
import bs4
import pytest


def test_layout_extend_with_default_slot():
    components = Tempered()
    components.add_template("a", """
        <div>
        {% slot %}
        </div>
    """)
    components.add_template("b", """
        {% extends "a" %}
        Test
    """)
    module = components.build_memory()
    soup = bs4.BeautifulSoup(module.b(), "html.parser")

    tag = soup.find("div")
    assert tag and "Test" in tag.text  # type:ignore


def test_layout_migrates_css():
    CSS_KEY = "TEMPERED_CSS"
    components = Tempered()
    components.add_template("a", """
        {%styles%}
        {% slot %}
    """)
    components.add_template("b", """
        {% extends "a" %}
        Test

        <style>
        a {
            content: """ + CSS_KEY + """;
        }
        </style>
    """)
    module = components.build_memory()
    soup = bs4.BeautifulSoup(module.b(), "html.parser")

    assert soup.find("style")
    assert CSS_KEY in soup.find("style").text  # type:ignore


@pytest.mark.xfail
def test_layout_extend_with_named_slots():
    components = Tempered()
    components.add_template("layout", """
        <title>{% slot title %}</title>
    """)
    components.add_template("child", """
        {% extends "layout" %}
        {% block title %}{% endblock %}
    """)

    module = components.build_memory()
    soup = bs4.BeautifulSoup(module.child(), "html.parser")
    assert soup.find("html")
    assert "Test" in soup.find("html").text  # type:ignore


@pytest.mark.xfail
def test_layout_extend_with_many_named_slots():
    components = Tempered()
    components.add_template("layout", """
        <a>{% slot b%}</a>
        <b>{% slot a%}</b>
    """)
    components.add_template("child", """
        {% extends "layout" %}
        {% block a %}A{% endblock %}
        {% block b %}B{% endblock %}
    """)

    module = components.build_memory()
    soup = bs4.BeautifulSoup(module.child(), "html.parser")
    assert soup.find("a").text == "A"  # type:ignore
    assert soup.find("b").text == "B"  # type:ignore
