from utils import build_templates
import pytest
import bs4
import tempered


def test_default_slot():
    component = build_templates(
        "{% layout 'layout' %}"
        "B"
    , (
        "layout",
        "<title>A{% slot %}C</title>",
    ))
    html = component()
    soup = bs4.BeautifulSoup(html)
    tag = soup.find("title")
    assert tag and "ABC" in tag.text


def test_single_named_slot():
    component = build_templates("""
        {% layout "layout" %}
        {% block title %}replace{%endblock%}
    """, ("layout", """
        <title>{% slot title%}{% endslot%}</title>
    """))

    soup = bs4.BeautifulSoup(component())
    tag = soup.find("title")
    assert tag and "replace" in tag.text


def test_single_named_required_slot():
    component = build_templates("""
        {% layout "layout" %}
        {% block title %}replace{%endblock%}
    """, ("layout", """
        <title>{% slot title required%}</title>
    """))

    soup = bs4.BeautifulSoup(component())
    tag = soup.find("title")
    assert tag and "replace" in tag.text


def test_single_named_slot_default():
    component = build_templates("""
        {% layout "layout" %}
    """, ("layout", """
        <title>{% slot title%}default value{% endslot%}</title>
    """))

    soup = bs4.BeautifulSoup(component())
    tag = soup.find("title")
    assert tag and "default value" in tag.text


def test_single_named_slot_replaces_default():
    component = build_templates("""
        {% layout "layout" %}
        {% block title %}replacement value{%endblock%}
    """, ("layout", """
        <title>{% slot title%}default value{% endslot%}</title>
    """))

    soup = bs4.BeautifulSoup(component())
    tag = soup.find("title")
    assert tag and "replacement value" in tag.text


def test_many_named_slots_replaces_default():
    component = build_templates("""
        {% layout "layout" %}
        {% block a %}A{%endblock%}
        {% block b %}B{%endblock%}
    """, ("layout", """
        <a>{% slot a required %}</a>
        <b>{% slot b %}B{% endslot %}</b>
        <c>{% slot c %}C{% endslot %}</c>
    """))

    soup = bs4.BeautifulSoup(component())
    assert soup.find("a") and "A" in soup.find("a").text
    assert soup.find("b") and "B" in soup.find("b").text
    assert soup.find("c") and "C" in soup.find("c").text
