import pytest
import tempered
from tests import build_template


def test_parameters_using_default():
    func = build_template("""
    <script type="tempered/metadata">
    parameters:
        foo:
            default: "'abc'"
    </script>
    {{ foo }}
    """)
    html = func()
    assert "abc" in html, html


def test_parameters_using_typing_extensions():
    build_template("""
    <script type="tempered/metadata">
    parameters:
        foo:
            type: t.Union[str, None]
            default: None
    </script>
    """)


def test_parameters_doesnt_allow_duplicates():
    with pytest.raises(tempered.ParserException):
        build_template("""
        <script type="tempered/metadata">
        parameters:
            foo: str
            foo: int
        </script>
        """)
