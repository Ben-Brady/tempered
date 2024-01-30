import typing_extensions as t

if t.TYPE_CHECKING:
    from .tempered import Tempered
else:
    Tempered = t.Any


def render(self: Tempered, name: str, **context: t.Any) -> str:
    return self.render_template(name, **context)
