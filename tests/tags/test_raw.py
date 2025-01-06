from tests import build_template


def test_text_isnt_escaped():
    component = build_template(
        """
            <t:html value="foo"></t:html>
    """
    )

    assert "<a>" in component(foo="<a>")


def test_string_literals_arent_transformed():
    component = build_template(
        """
        <style></style>
        <t:html value="'<a>'" ></t:html>
    """
    )

    assert "<a>" in component()
    assert "</a>" not in component()
