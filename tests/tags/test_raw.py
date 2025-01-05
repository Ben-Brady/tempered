from tests import build_template


def test_text_isnt_escaped():
    component = build_template(
        """
            <t:html value="foo" />
    """
    )

    assert "<a>" in component(foo="<a>")


def test_string_literals_arent_transformed():
    component = build_template(
        """
        <style></style>
        <t:html value="'<a>'" />
    """
    )

    assert "<a>" in component()
    assert "</a>" not in component()
