import sys
import bs4
from tests import build_template, test


@test("Numeric expressions work")
def _():
    component = build_template("{{ 2 + 3 }}")
    assert "5" in component()


@test("String expressions work")
def _():
    component = build_template("{{ 'a' + 'b' }}")
    assert "ab" in component()


@test("HTML tags are escaped")
def _():
    component = build_template("{{ '<script>' }}")
    assert "<script>" not in component()


@test("String literals aren't transformed")
def _():
    component = build_template(
        """
        <a href='{{ "/test" }}'>click</a>
    """
    )
    assert "/test" in component()


@test("Expression blocks allowed in attributes")
def _():
    link = "foo"
    component = build_template(
        """
        <a href='/bar/{{link}}'></a>
    """
    )
    html = component(link=link)
    a_tag = bs4.BeautifulSoup(html, "html.parser").find("a")
    assert isinstance(a_tag, bs4.Tag)
    assert "href" in a_tag.attrs
    assert a_tag.attrs["href"] == "/bar/foo"


@test("Expression blocks are escaped in attributes")
def _():
    link = "/test' onerror='alert(1)"
    component = build_template(
        """
        <a href='{{ link }}'></a>
    """
    )
    html = component(link=link)
    a_tag = bs4.BeautifulSoup(html, "html.parser").find("a")
    assert isinstance(a_tag, bs4.Tag), "Expression isn't escaped"
    assert "onerror" not in a_tag.attrs, "Expression isn't escaped"
    assert list(a_tag.attrs.keys()) == ["href"], "Expression isn't escaped"


@test("Multiple expressions ccombined")
def _():
    component = build_template(
        """
        1{{"a"}}2{{"b"}}3{{"c"}}
    """
    )
    assert "1a2b3c" in component()


@test("Expressions aren't limited by recursion limit")
def _():
    depth = sys.getrecursionlimit() + 10
    component = build_template("{{ 'a' }}" * depth)
    assert "a" in component()
