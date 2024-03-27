import pytest
import tempered
from tests import build_template, build_templates


def test_checks_detect_missing_layout():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_template('{% layout "dont_exist" %}')


def test_checks_detect_invalid_layout():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            '{% layout "non_layout" %}',
            ("non_layout", "This isn't a layout"),
        )


@pytest.mark.skip
def test_checks_detect_missing_components():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_template("{% component Invalid() %}")


@pytest.mark.skip
def test_checks_detect_missing_components_parameters():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            "{% component invalid() %}",
            ("invalid", "{% param a %}"),
        )


def test_checks_detect_invalid_blocks():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            """
            {% layout "layout" %}
            {% block nonexist %}
                This is invalid
            {% endblock %}
            """,
            ("layout", "{% slot exists %} {% endslot %}"),
        )


def test_checks_detect_missing_blocks():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            """
            {% layout "layout" %}
            {% block nonexist %}
                This is invalid
            {% endblock %}
            """,
            ("layout", "{% slot mandatory required %}"),
        )
