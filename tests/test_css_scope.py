import pytest
import tinycss2
from tempered.preprocess.scope import apply_scope_to_css


def assert_rule_transformed(scope: str, css: str, expected: str):
    def _normalise_css(css: str) -> str:
        return tinycss2.serialize(tinycss2.parse_stylesheet(css, skip_whitespace=True, skip_comments=True))

    scoped_css = apply_scope_to_css(css, scope)
    assert _normalise_css(scoped_css) == _normalise_css(expected)


def test_single_class():
    assert_rule_transformed(
        scope="scope",
        css=".div { }",
        expected=".div.scope { }"
    )


def test_single_ident():
    assert_rule_transformed(
        scope="scope",
        css="div { }",
        expected="div.scope { }"
    )


def test_two_classes():
    assert_rule_transformed(
        scope="scope",
        css=".a .b { }",
        expected=".a.scope .b.scope { }"
    )


def test_two_idents():
    assert_rule_transformed(
        scope="scope",
        css="a b { }",
        expected="a.scope b.scope { }"
    )


def test_class_and_psuedo():
    assert_rule_transformed(
        scope="scope",
        css=".a .b:hover() { }",
        expected=".a.scope .b.scope:hover() { }"
    )


@pytest.mark.skip
def test_many_classes():
    assert_rule_transformed(
        scope="scope",
        css=".a .b .c { }",
        expected=".a.scope .b .c.scope { }"
    )
