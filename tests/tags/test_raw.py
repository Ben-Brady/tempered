from tests import build_template


def test_text_isnt_escaped():
    component = build_template(
        """
        <t:html html="foo" />
    """
    )

    assert "<a>" in component(foo="<a>")


def test_string_literals_arent_transformed():
    component = build_template(
        """
        <style></style>
        <t:html html="'<a>'" />
    """
    )

    assert "<a>" in component()
    assert "</a>" not in component()
