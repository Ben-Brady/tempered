from utils import build_template, build_templates
import pytest
import tinycss2
import tempered


def test_components_can_have_optional_closing_tag():
    component = build_templates(
        """
            {<comp ()/>}
            {<comp ()>}
        """,
        ("comp", """
         test
        """)
    )

    html: str = component()
    assert html.count("test") == 2, html
