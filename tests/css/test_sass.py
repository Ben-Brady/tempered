from utils import build_template
import bs4
import pytest


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

