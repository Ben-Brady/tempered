from tests import build_template


def test_text_isnt_escaped():
    component = build_template(
        """
        {%param foo%}
        <style></style>
        {% html foo %}
    """
    )

    assert "<a>" in component(foo="<a>")


def test_string_literals_arent_transformed():
    component = build_template(
        """
        <style></style>
        {% html "<a>" %}
    """
    )

    assert "<a>" in component()
    assert "</a>" not in component()
