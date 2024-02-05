from __future__ import annotations
import zlib
from pathlib import Path
import typing_extensions as t
from . import module, parser, render


class Tempered:
    template_files: t.List[Path]
    "All list all the template files used, useful for hot reloading"
    generate_types: bool
    "If True, will generate dynamic type hints"
    static_folder: t.Optional[Path]
    "The static folder, if any"

    _module: module.TemperedModule
    _from_string_cache: t.Dict[str, t.Callable[..., str]]

    def __init__(
        self,
        template_folder: t.Union[str, Path, None] = None,
        static_folder: t.Union[str, Path, None] = None,
        *,
        generate_types: bool = True,
    ):
        self._from_string_cache = {}
        self.template_files = []
        self._module = module.TemperedModule()

        self.generate_types = generate_types
        if template_folder:
            self.add_template_folder(template_folder)
        if static_folder:
            self.static_folder = Path(static_folder)

    def add_global(self, name: str, value: t.Any):
        self._module.register_global(name, value)

    TFunc = t.TypeVar("TFunc", bound=t.Callable)
    def global_func(self, func: TFunc) -> TFunc:
        self._module.register_global(func.__name__, func)
        return func

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

        self._module.build_templates(templates)
        self._reconstruct_types()

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        self.template_files.append(file)

        name = str(file)
        html = file.read_text()
        template = parser.parse_template(name, html, file)
        self._module.build_templates([template])
        self._reconstruct_types()

    def add_template_from_string(self, name: str, html: str):
        template = parser.parse_template(name, html, file=None)
        self._module.build_templates([template])
        self._reconstruct_types()

    def add_templates_from_string(self, templates: t.Dict[str, str]):
        template_objs = [
            parser.parse_template(name, html, file=None)
            for name, html in templates.items()
        ]
        self._module.build_templates(template_objs)
        self._reconstruct_types()

    def render_from_string(self, html: str, **context: t.Any) -> str:
        if html in self._from_string_cache:
            func = self._from_string_cache[html]
            return func(**context)

        string_hash = hex(zlib.crc32(html.encode()))[2:]
        name = f"annonomous_{string_hash}>"
        parsed_template = parser.parse_template(name, html)
        self._module.build_templates([parsed_template])
        func = self._module.get_template_func(name)
        self._from_string_cache[html] = func
        return func(**context)

    def _render_template(self, name: str, **context: t.Any) -> str:
        func = self._module.get_template_func(name)
        return func(**context)

    # For dynamic type hinting, it's placed in an external file
    # def render_template(self, name: str, **context: t.Any) -> str:
    render_template = render.render_template

    def _reconstruct_types(self):
        if not self.generate_types:
            render.clear_types()
            return

        templates = self._module.get_templates()
        render.build_types(templates)
