from . import build_template
import bs4
import pytest


def test_component_uses_with_styles():
    CSS_KEY = "TEMPERED"
    CSS = f"a{{content:'{CSS_KEY}';}}"
    func = build_template(
        f"""
        <a>
            Bar!
        </a>
        <style>
            {CSS}
        </style>
    """
    )

    assert CSS_KEY in func(with_styles=True)
    assert CSS_KEY not in func(with_styles=False)


def test_template_places_styles():
    CSS_KEY = "TEMPERED"
    CSS = f"a{{content:'{CSS_KEY}';}}"
    func = build_template(
        f"""
        <head>
            {{% styles %}}
        </head>
        <style>
            {CSS}
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    style = soup.find("style")
    assert style and CSS_KEY in style.text


def test_empty_styles_arent_created():
    func = build_template(
        f"""
        {{% styles %}}
        <style>
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    assert soup.find("style") is None, html


def test_scss_styles_are_transpiled():
    func = build_template(
        """
        <style global lang="scss">
            a { b { color: red; }}
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    style = soup.find("style")
    assert style and style.text == "a b{color:red}"


def test_sass_styles_are_transpiled_with_indent():
    func = build_template(
        """
        <style global lang="sass">
            a
                b
                    color: red
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    style = soup.find("style")
    assert style and style.text == "a b{color:red}"


def test_html_scope_classes_applied_once():
    func = build_template(
        """
        <a>
        </a>
        <style>
            a { color: red; }
        </style>
        <style>
            a { font-weight: 1rem; }
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    style = soup.find("a")
    classes = style.attrs["class"]
    assert len(classes) == 1


def test_font_imports_arent_rearranged():
    FONT_URL = "https://fonts.googleapis.com/css?family=Open%20Sans:400"
    func = build_template(
        f"""
        <style>
            a {{ color: red; }}
        </style>
        <style>
            @import url('{FONT_URL}');
        </style>
    """
    )

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    style = soup.find("style")
    assert style
    assert style.text.startswith("@import")

