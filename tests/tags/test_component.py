from tests import build_templates, test
import pytest
from tempered import Tempered, InvalidTemplateException

@test("Components prevent css duplication")
def _():
    CSS_KEY = "TEMPERED"
    component = build_templates(
        """
            <script type="tempered/metadata">
            imports:
                Child: child
            </script>

            <t:Child></t:Child>
            <t:Child></t:Child>
        """,
        (
            "child",
            f"""
         <a>test</a>
         <style>
            a {{ color: {CSS_KEY}; }}
         </style>
        """,
        ),
    )
    html: str = component()
    assert html.count(CSS_KEY) == 1, html


@test("Components account for nested children")
def _():
    CSS_KEY = "TEMPERED"

    MAIN_TEMPLATE = """
    <script type="tempered/metadata">
    imports:
        A: a
    </script>

    <t:A/>
    """
    A_TEMPLATE = """
    <script type="tempered/metadata">
    imports:
        B: b
    </script>

    <t:B/>
    """
    B_TEMPLATE = """
    <script type="tempered/metadata">
    imports:
        C: c
    </script>

    <t:C/>
    """
    C_TEMPLATE = """
    <script type="tempered/metadata">
    imports:
        D: d
    </script>

    <t:D/>
    """
    D_TEMPLATE = f"<style>a {{ color: {CSS_KEY}; }}</style>"

    component = build_templates(
        MAIN_TEMPLATE,
        ("a", A_TEMPLATE),
        ("b", B_TEMPLATE),
        ("c", C_TEMPLATE),
        ("d", D_TEMPLATE),
    )
    html = component()
    assert html.count(CSS_KEY) == 1, html


@test("Components accept parameters")
def _():
    component = build_templates(
        """
        <script type="tempered/metadata">
        imports:
            Computed: computed
        </script>

        <t:Computed foo="'bar'" />
        """,
        ("computed", "{{foo}}{{foo}}"),
    )
    html = component()
    assert "t:" not in html
    assert "barbar" in html


@test("Components allow default parameters")
def _():
    tempered = Tempered()
    tempered.add_from_string("computed.html", '''
        <script type="tempered/metadata">
        parameters:
            foo:
                type: str
                default: "'bar'"
        </script>
        {{foo}}{{bar}}
    ''')

    html = tempered.render_string('''
        <script type="tempered/metadata">
        imports:
            Computed: computed.html
        </script>

        <t:Computed />
    ''', bar="bar")
    assert "barbar" in html, html


@test("Components allows mixed parameters")
def _():
    component = build_templates(
        """
        <script type="tempered/metadata">
        imports:
            Computed: computed.html
        </script>

        <t:Computed bar="'bar'"/>
        """,
        (
            "computed.html",
            """
            <script type="tempered/metadata">
            parameters:
                foo:
                    type: str
                    default: "'foo'"
                bar: str
            </script>
            {{foo}}-{{bar}}
            """,
        ),
    )
    html = component()
    assert "foo-bar" in html


@test("Raised invalid template on unimported component")
def _():
    with pytest.raises(InvalidTemplateException):
        build_templates("""<t:Computed bar="'bar'"/>""")
