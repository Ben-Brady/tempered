from tests import build_template, test


@test("Range loops are valid")
def _():
    component = build_template(
        """
        <t:for for="x" in="range(5)">{{ x }}</t:for>
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html



@test("For each loops are valid")
def _():
    component = build_template(
        """
        <t:for for="item" in="items">{{ item }}</t:for>
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

        <t:for for="key, value" in="foo.items()">
            {{ key }}={{ value}}
        </t:for>

    """
    )
    html = component(foo={"a": 1,"b": 2})
    assert "a=1" in html
    assert "b=2" in html


@test("Empty for loops are valid")
def _():
    component = build_template(
        """
        <t:for for="x" in="range(5)"></t:for>
    """
    )
    component()


@test("Optimisable loops are valid")
def _():
    component = build_template(
        """
        <t:for for="x" in="range(5)">
            {{ x }}
        </t:for>
    """
    )
    html = component()
    for i in range(5):
        assert str(i) in html


@test("Nested loops are valid")
def _():
    component = build_template(
        """
        <t:for for="x" in="range(2)">
            <t:for for="y" in="range(2)">
                ({{x}},{{y}})
            </t:for>
        </t:for>
    """
    )
    html = component()

    for x in range(2):
        for y in range(2):
            assert f"({x},{y})" in html


@test("Setting variables inside a for loop is valid")
def _():
    component = build_template(
        """
        <t:for for="x" in="range(5)">
            <t:for for="y" in="range(5)">
                <script type="tempered/python">
                    squared = x * y
                </script>
                {{ squared }}
            </t:for>
        </t:for>
    """
    )
    html = component()
    for i in range(5):
        assert str(i * i) in html


@test("Nested loops with identical names act correctly")
def _():
    component = build_template(
        """

        <t:for for="x" in="range(5)">
            <t:for for="x" in="range(5)">
                {{x}}
            </t:for>
        </t:for>

    """
    )
    html = component()

    for x in range(5):
        assert html.count(str(x)) == 5


@test("Multiple loops with identical names act correctly")
def _():
    component = build_template("""
        <t:for for="x" in="range(5)">
            {{ x }}
        </t:for>
        <t:for for="x" in="range(5)">
            {{ x }}
        </t:for>
    """)
    html = component()

    assert html.count("01234") == 2, html
