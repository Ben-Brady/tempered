from utils import build_template


def test_strings_arent_transformed():
    component = build_template("""
        <style></style>
        {% html "<a>" %}
    """)

    assert "<a>" in component()
    assert "</a>" not in component()

