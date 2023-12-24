from utils import build_template
import bs4
import sys
import pytest


def test_simple_expr_works():
    component = build_template("{{ 123 }}")
    assert "123" in component()


def test_html_tags_are_escaped():
    component = build_template("{{ '<script>' }}")
    assert "<script>" not in component()


def test_string_literals_arent_transformed():
    component = build_template(
        """
        <a href='{{ "/test" }}'>click</a>
    """
    )
    assert "/test" in component()


def test_expr_block_escapes_param():
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


def test_multiple_expr_chained():
    component = build_template(
        """
        1{{"a"}}2{{"b"}}3{{"c"}}
    """
    )
    assert "1a2b3c" in component()


def test_many_expr_chained():
    depth = sys.getrecursionlimit() + 10
    component = build_template("{{ 'a' }}" * depth)
    assert "a" in component()
