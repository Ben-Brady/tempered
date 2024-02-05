from . import build_template, build_templates


def test_variables_are_converted_to_kwargs():
    func = build_template(
        """
        {% param a: int %}
        {{ a }}
        {{ b }}
    """
    )
    html = func(a="TEMPERED_A", b="TEMPERED_B")
    assert "TEMPERED_A" in html
    assert "TEMPERED_B" in html


def test_kwargs_passed_to_layout():
    func = build_templates(
        """
        {% layout "layout" %}
        """,
        (
            "layout",
            """
         {% slot %}
         {{ foo }}
         """,
        ),
    )

    assert "TEMPERED" in func(foo="TEMPERED")


def test_kwargs_passed_to_component():
    func = build_templates(
        """
        {% import Child from "child" %}
        {% component Child() %}
        """,
        ("child", "{{ foo }}"),
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
        {% for x in range(3) %}
            {{ x }}
        {% endfor %}
        {{ x }}
    """
    )
    html = func(x="TEMPERED")
    assert "2" in html
    assert "TEMPERED" in html


def test_kwargs_loop_variable():
    func = build_template(
        """
        {% for x in items %}
            {{ x }}
        {% endfor %}
    """
    )
    items = ["a", "b", "c"]
    html = func(items=items)
    for item in items:
        assert item in html
