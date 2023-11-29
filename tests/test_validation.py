import tempered
import utils
import pytest


def test_checks_detect_missing_layout():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_template('{% layout "dont_exist" %}')


def test_checks_detect_invalid_layout():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_templates(
            '{% layout "non_layout" %}',
            ("non_layout", "This isn't a layout"),
        )


def test_checks_detect_missing_components():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_template(
            """
            {<Invalid()>}
        """
        )


def test_checks_detect_missing_components_parameters():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_templates(
            "{<invalid()>}",
            ("invalid", "{% param a %}"),
        )


def test_checks_detect_invalid_blocks():
    with pytest.raises(tempered.errors.InvalidTemplate):
        utils.build_templates(
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
        utils.build_templates(
            """
            {% layout "layout" %}
            {% block nonexist %}
                This is invalid
            {% endblock %}
            """,
            ("layout", "{% slot mandatory required %}"),
        )
