from __future__ import annotations
import zlib
from pathlib import Path
import typing_extensions as t
from .template import parse_template
from . import module, parsing, types

class TemperedBase:
    template_files: t.List[Path]
    static_folder: t.Optional[Path]
    _module: module.TemperedModule
    _from_string_cache: t.Dict[str, t.Callable[..., str]]
    _generate_types: bool

    def __init__(self, *, template_folder: t.Union[str, Path, None]=None, static_folder: t.Union[str, Path, None]=None, generate_types: bool=True):
        ...

    def add_from_file(self, file: t.Union[Path, str]):
        ...

    def add_from_folder(self, folder: t.Union[Path, str]):
        ...

    def add_from_string(self, name: str, html: str):
        ...

    def add_mapping(self, templates: t.Mapping[str, str]):
        ...

    def render_string(self, html: str, **context: t.Any) -> str:
        ...

    def render(self, name: str, **context: t.Any) -> str:
        ...

    def add_global(self, name: str, value: t.Any):
        ...
    _has_cleared_types = False

    def _reconstruct_types(self):
        ...

class Tempered(TemperedBase):
    template_files: t.List[Path]
    '\n    A readonly list of the any files used in templates.\n\n    This is useful for watchdog and code refreshing tools.\n\n    **Example in Flask**\n\n    ```python\n    app = Flask()\n\n    if __name__ == "__main__":\n        app.run(\n            extra_files=tempered.template_files,\n            # Flask now reloads when a template changes\n        )\n    ```\n    '

    def __init__(self, *, template_folder: t.Union[str, Path, None]=None, static_folder: t.Union[str, Path, None]=None, generate_types: bool=True, **context):
        ...

    def add_from_file(self, file: t.Union[Path, str]):
        ...

    def add_from_folder(self, folder: t.Union[Path, str]):
        ...

    def add_from_string(self, name: str, html: str):
        ...

    def add_mapping(self, templates: t.Mapping[str, str]):
        ...

    @t.overload
    def render(self, name: t.Literal['main'], **context: t.Any) -> str:
        ...

    def render(self, name: str, **context: t.Any) -> str:
        ...

    def render_string(self, html: str, **context: t.Any) -> str:
        ...

    def add_global(self, name: str, value: t.Any):
        ...