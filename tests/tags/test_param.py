import pytest
import tempered
from tests import build_template


def test_param_using_typing_extensions():
    build_template("{% param foo: t.Union[str, None] = None %}")


def test_param_doesnt_allow_duplicates():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_template("{% param foo %} {% param foo %}")
