import tempered
import utils
import pytest


def test_checks_detect_invalid_layout():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_template("""
            {% layout "dont_exist" %}
        """)


def test_checks_detect_missing_components():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_template("""
            {<Invalid()>}
        """)

