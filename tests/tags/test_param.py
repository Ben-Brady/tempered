import pytest
import tempered
from tests import build_template


def test_param_using_typing_extensions():
    build_template("""
    <script type="tempered/metadata">
    parameters:
        foo:
            type: t.Union[str, None]
            default: None
    </script>
    """)


def test_param_doesnt_allow_duplicates():
    with pytest.raises(tempered.ParserException):
        build_template("""
        <script type="tempered/metadata">
        parameters:
            foo: str
            foo: int
        </script>
        """)
