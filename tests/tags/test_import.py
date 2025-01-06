import pytest
import tempered
from ..utils import build_templates


def test_importing_components():
    render = build_templates(
        """
        <script type="tempered/metadata">
        imports:
            Foo: foo
        </script>

        <t:Foo></t:Foo>
    """,
        ("foo", """Hello World"""),
    )

    assert "Hello World" in render()


def test_importing_components_with_non_ident_names():
    render = build_templates(
        """
        <script type="tempered/metadata">
        imports:
            Foo: components/foo.html
        </script>

        <t:Foo></t:Foo>
    """,
        ("components/foo.html", """Hello World"""),
    )

    assert "Hello World" in render()


@pytest.mark.skip
def test_raise_error_on_invalid_import():
    with pytest.raises(tempered.InvalidTemplateException):
        build_templates(
            """
            <script type="tempered/metadata">
            imports:
                Foo: components/foo.html
            </script>

            <t:Foo></t:Foo>
        """,
            ("bar", "Hello World"),
        )
