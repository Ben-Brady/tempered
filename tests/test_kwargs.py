from tests import build_template, build_templates


def test_variables_are_converted_to_kwargs():
    func = build_template(
        """
        <script type="metadata/tempered">
        parameters:
            a: int
        </script>

        {{ a }}
        {{ b }}
    """
    )
    html = func(a="TEMPERED_A", b="TEMPERED_B")
    assert "TEMPERED_A" in html
    assert "TEMPERED_B" in html


def test_kwargs_passed_to_layout():
    content = """
        <script type="tempered/metadata">
        layout: layout.html
        </script>
        """

    func = build_templates(
        content,
        ("layout.html", "<t:slot></t:slot>{{ foo }}"),
    )

    assert "TEMPERED" in func(foo="TEMPERED")


def test_kwargs_lets_you_pass_functions():
    func = build_template(
        """
        {{ format_number(2000) }}
    """
    )
    assert "2,000" in func(format_number=lambda x: f"{x:,}")


def test_kwargs_dont_affect_for_loops():
    func = build_template(
        """
        <t:for for="x" in="range(3)">
            {{ x }}
        </t:for>
        {{ x }}
    """
    )
    html = func(x="TEMPERED")
    assert "2" in html
    assert "TEMPERED" in html


def test_kwargs_loop_variable():
    func = build_template(
        """
        <t:for for="x" in="items">
            {{ x }}
        </t:for>
    """
    )
    items = ["a", "b", "c"]
    html = func(items=items)
    for item in items:
        assert item in html
