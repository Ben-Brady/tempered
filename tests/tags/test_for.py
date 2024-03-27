from tests import build_template, test


@test("Range loops are valid")
def _():
    component = build_template(
        """
        {% for x in range(5) %}{{ x }}{% endfor %}
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html



@test("For each loops are valid")
def _():
    component = build_template(
        """
        {% for item in items %}{{ item }}{% endfor %}
    """
    )
    items = ["a", "b", "c"]
    html = component(items=items)
    for item in items:
        assert item in html


@test("For loops with multiple targets")
def _():
    component = build_template(
        """
        {% for key, value in foo.items() %}
            {{ key }}={{ value}}
        {% endfor %}
    """
    )
    html = component(foo={"a": 1})
    assert "a=1" in html



@test("Empty for loops are valid")
def _():
    component = build_template(
        """
        {% for x in range(5) %}{% endfor %}
    """
    )
    component()


@test("Optimisable loops are valid")
def _():
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


@test("Setting variables inside a for loop is valid")
def _():
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


@test("Nested loops are valid")
def _():
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


@test("Nested loops with identical names act correctly")
def _():
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


@test("Multiple loops with identical names act correctly")
def _():
    component = build_template(
        """
        {% for x in range(5) %}{{x}}{% endfor %}
        {% for x in range(5) %}{{x}}{% endfor %}
    """
    )
    html = component()

    assert html.count("01234") == 2, html
