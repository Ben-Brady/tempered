import bs4
from tests import build_templates


def test_layout_extend_with_default_slot():
    func = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout.html
        </script>

        Test
        """,
        ("layout.html", "<div><t:slot/></div>"),
    )

    html = func()
    soup = bs4.BeautifulSoup(html, "html.parser")

    tag = soup.find("div")
    assert tag and "Test" in tag.text, html  # type:ignore


def test_layout_migrates_css():
    CSS_KEY = "TEMPERED_CSS"

    func = build_templates(
        f"""
        <script type"tempered/metadata">
        layout: layout.html
        </script>

        Test
        <style>
        a {{ content: '{CSS_KEY}'; }}
        </style>
        """,
        ("layout.html", "<t:styles/> <t:slot/>"),
    )
    html = func()
    soup = bs4.BeautifulSoup(html, "html.parser")

    assert soup.find("style")
    assert CSS_KEY in soup.find("style").text  # type:ignore


def test_layout_extend_with_named_slots():
    func = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout.html
        </script>

        <t:block name="title">Test</t:block>
        """,
        ("layout.html", "<title><t:slot name='title' required></t:slot></title>"),
    )
    soup = bs4.BeautifulSoup(func(), "html.parser")
    assert soup.find("title")
    assert "Test" in soup.find("title").text  # type:ignore


def test_layout_extend_with_many_named_slots():
    func = build_templates(
        """
        <script type="tempered/metadata">
            layout: layout.html
        </script>

        <t:block name="a">A</t:block>
        <t:block name="b">B</t:block>
        """,
        (
            "layout.html",
            """
                <a>
                    <t:slot name="a" required></t:slot>
                </a>
                <b>
                    <t:slot name="b" required></t:slot>
                </b>
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
        <script type="tempered/metadata">
        layout: layout.html
        </script>
        """,
        (
            "layout.html",
            f"""
                <t:styles></t:styles>
                <t:slot></t:slot>

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
    CSS_COMP = "TEMPERED_COMPONENT"
    component = f"""
        <script type="tempered/metadata">
        layout: layout.html
        </script>

        <style>
            a {{content: '{CSS_COMP}'; }}
        </style>
    """
    layout = f"""
        <t:styles />
        <t:slot />
        <style>
            a {{ content: '{CSS_LAYOUT}'; }}
        </style>
    """

    func = build_templates(
        component,
        ("layout.html", layout),
    )
    styled_html = func(with_styles=True)
    styled_html = func(with_styles=True)
    assert CSS_LAYOUT in styled_html, "Layout css not found"
    assert CSS_COMP in styled_html, "Component css not found"


def test_nested_layout_styles_are_combined():
    CSS_LAYOUT_1 = "TEMPERED_LAYOUT_1"
    CSS_LAYOUT_2 = "TEMPERED_LAYOUT_2"
    CSS_COMP = "TEMPERED_COMPONENT"
    COMPONENT = f"""
        <script type="tempered/metadata">
        layout: "layout_1"
        </script>

        <style>
            a {{content: '{CSS_COMP}'; }}
        </style>
    """
    layout_1 = f"""
        <script type="tempered/metadata">
        layout: "layout_2"
        </script>

        <t:styles></t:styles>
        <t:slot></t:slot>

        <style>
            a {{ content: '{CSS_LAYOUT_1}'; }}
        </style>
    """

    layout_2 = f"""
        <t:styles></t:styles>
        <t:slot></t:slot>
        <style>
            a {{ content: '{CSS_LAYOUT_2}'; }}
        </style>
    """

    func = build_templates(
        COMPONENT,
        ("layout_1", layout_1),
        ("layout_2", layout_2),
    )
    styled_html = func(with_styles=True)
    assert CSS_LAYOUT_1 in styled_html, "Layout 1 css not found"
    assert CSS_LAYOUT_2 in styled_html, "Layout 2 css not found"
    assert CSS_COMP in styled_html, "Component's css not found"
