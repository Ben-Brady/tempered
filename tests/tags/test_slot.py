import bs4
from tests import build_templates


def test_default_slot():
    component = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout
        </script>
        B
        """,
        (
            "layout",
            "<title>A<t:slot />C</title>",
        ),
    )
    html = component()
    soup = bs4.BeautifulSoup(html, features="html.parser")
    tag = soup.find("title")
    assert tag and "ABC" in tag.text


def test_single_named_slot():
    component = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout
        </script>

        <t:block name='title'>
            replace
        </t:block>
    """,
        (
            "layout",
            """
        <title><t:slot name='title'/></title>
    """,
        ),
    )

    soup = bs4.BeautifulSoup(component(), features="html.parser")
    tag = soup.find("title")
    assert tag and "replace" in tag.text


def test_single_named_required_slot():
    component = build_templates(
        """

        <script type="tempered/metadata">
        layout: layout
        </script>
        <t:block name='title'>replace</t:block>
    """,
        (
            "layout",
            """
        <title><t:slot name='title' required /></title>
    """,
        ),
    )

    soup = bs4.BeautifulSoup(component(), features="html.parser")
    tag = soup.find("title")
    assert tag and "replace" in tag.text


def test_single_named_slot_default():
    component = build_templates("""
        <script type="tempered/metadata">
        layout: layout
        </script>
        """,
        ("layout", "<title><t:slot name='title'>default value</t:slot></title>"),
    )

    soup = bs4.BeautifulSoup(component(), features="html.parser")
    tag = soup.find("title")
    assert tag and "default value" in tag.text


def test_single_named_slot_replaces_default():
    component = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout
        </script>

        <t:block name='title'>replacement value</t:block>
    """,
        (
            "layout",
            """
        <title><t:slot name='title'>default value</t:slot></title>
    """,
        ),
    )

    soup = bs4.BeautifulSoup(component(), features="html.parser")
    tag = soup.find("title")
    assert tag and "replacement value" in tag.text


def test_many_named_slots_replaces_default():
    component = build_templates(
        """
        <script type="tempered/metadata">
        layout: layout
        </script>
        <t:block name='a'>A</t:block>
        <t:block name='b'>B</t:block>
    """,
        (
            "layout",
            """
        <a><t:slot name='a' required ></t:slot></a>
        <b><t:slot name='b'>B</t:slot></b>
        <c><t:slot name='c'>C</t:slot></c>
    """,
        ),
    )

    soup = bs4.BeautifulSoup(component(), features="html.parser")
    assert soup.find("a") and "A" in soup.find("a").text  # type: ignore
    assert soup.find("b") and "B" in soup.find("b").text  # type: ignore
    assert soup.find("c") and "C" in soup.find("c").text  # type: ignore
