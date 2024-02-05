from . import build_template


def test_empty_for_loop():
    component = build_template(
        """
        {% for x in range(5) %}{% endfor %}
    """
    )
    component()


def test_for_range_loop():
    component = build_template(
        """
        {% for x in range(5) %}{{ x }}{% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html


def test_for_loop_multiple_targets_loop():
    component = build_template(
        """
        {% for key, value in foo.items() %}
            {{ key }}={{ value}}
        {% endfor %}
    """
    )
    html = component(foo={"a": 1})
    assert "a=1" in html


def test_for_each_loop():
    component = build_template(
        """
        {% for item in items %}{{ item }}{% endfor %}
    """
    )
    items = ["a", "b", "c"]
    html = component(items=items)
    for item in items:
        assert item in html


def test_for_range_loop_with_unroll():
    component = build_template(
        """
        {% for x in range(5) %}
            {{ x }}
        {% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html


def test_for_loop_with_set():
    component = build_template(
        """
        {% for x in range(5) %}
            {% set squared = x * x %}
            {{ squared }}
        {% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i * i) in html


def test_nested_for_loop():
    component = build_template(
        """
        {% for x in range(2) %}
            {% for y in range(2) %}
                ({{x}},{{y}})
            {% endfor %}
        {% endfor %}
    """
    )
    html = component()

    for x in range(2):
        for y in range(2):
            assert f"({x},{y})" in html


def test_nested_for_loop_with_same_name():
    component = build_template(
        """
        {% for x in range(5) %}
            {% for x in range(5) %}
                {{x}}
            {% endfor %}
        {% endfor %}
    """
    )
    html = component()

    for x in range(5):
        assert html.count(str(x)) == 5
