from . import build_template
import pytest
import bs4
import tempered


def test_param_using_typing_extensions():
    build_template("{% param foo: t.Union[str, None] = None %}")
