import typing_extensions as t
from tempered import Tempered


def build_template(
    template: str,
    globals: t.Dict[str, t.Any],
) -> t.Callable[..., str]:
    tempered = Tempered()
    tempered.add_template_from_string("test", template)
    for name, value in globals.items():
        tempered.add_global(name, value)
    env = tempered.build_enviroment(generate_types=False)
    template_obj = env.get_template("test")
    assert template_obj
    return template_obj.render


def test_globals_are_accessble_in_templates():
    globals = {
        "format_str": lambda name: f"Hello {name}!",
    }
    template = "{{format_str('Ben')}}"
    render = build_template(template, globals)
    assert render() == "Hello Ben!"


def test_globals_dont_override_locals():
    globals = {"text": "Foo"}
    locals = {"text": "Bar"}
    template = "{{ text }}"
    render = build_template(template, globals)
    assert render(**locals) == "Bar"


def test_enviroment_globals_used_in_templates():
    tempered = Tempered()
    tempered.add_template_from_string("test", "{{ text }}")
    tempered.add_global("text", "Foo")
    env = tempered.build_enviroment(generate_types=False)
    template = env.get_template("test")
    assert template is not None
    assert template.render() == "Foo"


def test_enviroment_globals_dont_override_locals():
    tempered = Tempered()
    tempered.add_template_from_string("test", "{{ text }}")
    tempered.add_global("text", "Foo")
    env = tempered.build_enviroment(generate_types=False)
    template = env.get_template("test")
    assert template is not None
    assert template.render(text="Bar") == "Bar"
