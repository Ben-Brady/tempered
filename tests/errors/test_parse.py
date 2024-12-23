import pytest
import tempered
from tempered.src.template.template import parse_template


def test_invalid_end_block():
    with pytest.raises(tempered.ParserException):
        parse_template("foo", "{% block test %}{%endblock test%}")


def test_invalid_tag():
    with pytest.raises(tempered.ParserException):
        parse_template("foo", "{% fake %}")
