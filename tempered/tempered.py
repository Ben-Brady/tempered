from __future__ import annotations
import zlib
from pathlib import Path
from types import ModuleType
import typing_extensions as t
from . import build, parser

BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _module: ModuleType
    _from_string_cache: t.Dict[str, t.Callable[..., str]]
    template_files: t.List[Path]

    def __init__(self, template_folder: t.Union[str, Path, None] = None):
        self._from_string_cache = {}
        self._module = build.build_intial_module()
        if template_folder:
            self.add_template_folder(template_folder)

    def add_global(self, name: str, value: t.Any):
        build.register_global(self._module, name, value)

    def add_template_folder(self, folder: t.Union[Path, str]):
        folder = Path(folder)
        FOLDER_PREFIX = f"{folder}/"
        templates = []
        for file in folder.glob("**/*.*"):
            name = str(file)
            name = name[len(FOLDER_PREFIX) :]
            html = file.read_text()
            template = parser.parse_template(name, html, file)
            templates.append(template)

        build.build_templates(self._module, templates)

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        name = str(file)
        html = file.read_text()
        template = parser.parse_template(name, html, file)
        build.build_templates(self._module, [template])

    def add_template_from_string(self, name: str, html: str):
        template = parser.parse_template(name, html, file=None)
        build.build_templates(self._module, [template])

    def add_templates_from_string(self, templates: t.Dict[str, str]):
        template_objs = [
            parser.parse_template(name, html, file=None)
            for name, html in templates.items()
        ]
        build.build_templates(self._module, template_objs)

    def render_from_string(self, html: str, **context: t.Any) -> str:
        if html in self._from_string_cache:
            return self._from_string_cache[html](**context)

        string_hash = hex(zlib.crc32(html.encode()))[2:]
        name = f"annonomous_{string_hash}>"
        parsed_template = parser.parse_template(name, html)
        build.build_templates(self._module, [parsed_template])
        return self.render_template(name, **context)

    def render_template(self, template_name: str, **context: t.Any) -> str:
        func = build.get_template_func(self._module, template_name)
        return func(**context)
