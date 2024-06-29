from functools import partial
import typing_extensions as t
from tempered import Tempered


def build_template(
    template: str,
    globals: t.Dict[str, t.Any],
) -> t.Callable[..., str]:
    tempered = Tempered()
    tempered.add_from_string("test", template)
    for name, value in globals.items():
        tempered.add_global(name, value)

    return partial(tempered.render, "test")


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
