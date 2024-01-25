from tempered import Tempered
from tempered.types import TYPES_FILE


def test_types_are_created():
    if TYPES_FILE.exists():
        TYPES_FILE.unlink()

    tempered = Tempered()
    tempered.add_template_from_string(
        "profile",
        '{% param name: str = "Ben Brady" %}',
    )

    assert not TYPES_FILE.exists()
    tempered.build_enviroment(generate_types=True)
    assert TYPES_FILE.exists()


def test_types_are_valid_python():
    import ast

    tempered = Tempered()
    tempered.add_template_from_string(
        "profile",
        '{% param name: str = "Ben Brady" %}',
    )
    tempered.build_enviroment(generate_types=True)
    source = TYPES_FILE.read_text()
    ast.parse(source)


def test_get_template_on_nonexist_template_returns_None():
    tempered = Tempered()
    tempered.add_template_from_string(
        "profile",
        '{% param name: str = "Ben Brady" %}',
    )
    env = tempered.build_enviroment(generate_types=True)
    assert env.get_template("foo") is None


def test_get_template_returns_templates():
    tempered = Tempered()
    tempered.add_template_from_string(
        "profile",
        """
        {% param name: str = "Ben" %}
        {% param foo: t.Dict[str, None] = "Ben" %}
    """,
    )
    env = tempered.build_enviroment(generate_types=True)
    assert env.get_template("profile") is not None


def test_enviroment_templates_render_correctly():
    tempered = Tempered()
    tempered.add_template_from_string(
        "profile",
        """
        {% param name: str = "Ben" %}
        Hello {{ name }}
    """,
    )
    env = tempered.build_enviroment(generate_types=True)
    output = env.get_template("profile").render(name="Dave")
    assert "Hello Dave" in output


def test_enviroment_from_string():
    env = Tempered().build_enviroment()
    template = env.from_string("<div>{{ x }}</div>")
    html = template.render(x=1)
    assert html == "<div>1</div>"
