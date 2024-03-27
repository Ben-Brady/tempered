import bs4
from tests import build_templates


def test_layout_extend_with_default_slot():
    func = build_templates(
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

    func = build_templates(
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
    func = build_templates(
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
    func = build_templates(
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
    func = build_templates(
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

    func = build_templates(
        component,
        ("layout", layout),
    )
    styled_html = func(with_styles=True)
    styled_html = func(with_styles=True)
    assert CSS_LAYOUT in styled_html, "Layout css not found"
    assert CSS_COMP in styled_html, "Component css not found"


def test_nested_layout_styles_are_combined():
    CSS_LAYOUT_1 = "TEMPERED_LAYOUT"
    CSS_LAYOUT_2 = "TEMPERED_LAYOUT"
    CSS_COMP = "TEMPERED_COMP"
    layout_1 = f"""
        {{% styles %}}
        {{% slot %}}
        <style>
            a {{ content: '{CSS_LAYOUT_1}'; }}
        </style>
    """
    layout_2 = f"""
        {{% layout "layout_1" %}}
        {{% styles %}}
        {{% slot %}}
        <style>
            a {{ content: '{CSS_LAYOUT_2}'; }}
        </style>
    """
    component = f"""
        {{% layout "layout_2" %}}
        <style>
            a {{content: '{CSS_COMP}'; }}
        </style>
    """

    func = build_templates(
        component,
        ("layout_1", layout_1),
        ("layout_2", layout_2),
    )
    styled_html = func(with_styles=True)
    assert CSS_LAYOUT_1 in styled_html, "Layout 1 css not found"
    assert CSS_LAYOUT_2 in styled_html, "Layout 2 css not found"
    assert CSS_COMP in styled_html, "Component's css not found"
