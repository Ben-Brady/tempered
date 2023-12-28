from tempered import Tempered
import typing_extensions as t


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
