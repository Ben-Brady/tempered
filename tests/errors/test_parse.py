import pytest
import tempered
from tempered.src.template.template import parse_template


def test_invalid_end_block():
    with pytest.raises(tempered.InvalidTemplateException):
        parse_template("foo", "<t:block name='test'></t:block>")
