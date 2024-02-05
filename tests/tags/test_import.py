import pytest
import tempered
from ..utils import build_templates


def test_importing_components():
    render = build_templates(
        """
        {% import Foo from "foo" %}
        {% component Foo() %}
    """,
        ("foo", """Hello World"""),
    )

    assert "Hello World" in render()


def test_importing_components_with_non_ident_names():
    render = build_templates(
        """
        {% import Foo from "components/foo.html" %}
        {% component Foo() %}
    """,
        ("components/foo.html", """Hello World"""),
    )

    assert "Hello World" in render()


@pytest.mark.skip
def test_raise_error_on_invalid_import():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            """
            {% import Foo from "foo" %}
            {% component Foo() %}
        """,
            ("bar", "Hello World"),
        )
