from ..utils import build_templates
import tempered
import pytest


@pytest.mark.skip
def test_importing_components():
    render = build_templates(
        """
        {% import Foo from "foo" %}
        {<Foo/>}
    """,
        ("foo", """Hello World"""),
    )

    assert "Hello World" in render()


@pytest.mark.skip
def test_raise_error_on_invalid_import():
    with pytest.raises(tempered.errors.InvalidTemplate):
        build_templates(
            """
            {% import Foo from "foo" %}
            {<Foo/>}
        """,
            ("bar", """Hello World"""),
        )
