from __future__ import annotations
import zlib
from pathlib import Path
from types import ModuleType
import typing_extensions as t
from . import build, parser, render

BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    template_files: t.List[Path]
    "All list all the template files used, useful for hot reloading"
    generate_types: bool
    "If True, will generate dynamic type hints"

    _module: ModuleType
    _from_string_cache: t.Dict[str, t.Callable[..., str]]

    def __init__(
        self,
        template_folder: t.Union[str, Path, None] = None,
        *,
        generate_types: bool = True,
    ):
        self._from_string_cache = {}
        self.template_files = []
        self.generate_types = generate_types
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
            self.template_files.append(file)
            name = str(file)
            name = name[len(FOLDER_PREFIX) :]
            html = file.read_text()
            template = parser.parse_template(name, html, file)
            templates.append(template)

        build.build_templates(self._module, templates)
        self._reconstruct_types()

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        self.template_files.append(file)

        name = str(file)
        html = file.read_text()
        template = parser.parse_template(name, html, file)
        build.build_templates(self._module, [template])
        self._reconstruct_types()

    def add_template_from_string(self, name: str, html: str):
        template = parser.parse_template(name, html, file=None)
        build.build_templates(self._module, [template])
        self._reconstruct_types()

    def add_templates_from_string(self, templates: t.Dict[str, str]):
        template_objs = [
            parser.parse_template(name, html, file=None)
            for name, html in templates.items()
        ]
        build.build_templates(self._module, template_objs)
        self._reconstruct_types()

    def render_from_string(self, html: str, **context: t.Any) -> str:
        if html in self._from_string_cache:
            func = self._from_string_cache[html]
            return func(**context)

        string_hash = hex(zlib.crc32(html.encode()))[2:]
        name = f"annonomous_{string_hash}>"
        parsed_template = parser.parse_template(name, html)
        build.build_templates(self._module, [parsed_template])
        func = build.get_template_func(self._module, name)
        self._from_string_cache[html] = func
        return func(**context)

    def _render_template(self, name: str, **context: t.Any) -> str:
        func = build.get_template_func(self._module, name)
        return func(**context)

    render_template = render.render_template

    def _reconstruct_types(self):
        if not self.generate_types:
            render.clear_types()
            return

        render.build_types(build.get_templates(self._module))
