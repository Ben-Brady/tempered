from pathlib import Path
import typing_extensions as t
from . import build, parser, types
from .compiler.constants import template_func_name
from .enviroment import Environment, Template
from types import ModuleType


BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _module: ModuleType
    template_files: t.List[Path]

    def __init__(self, template_folder: t.Union[str, Path, None] = None):
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

    def build_enviroment(self, generate_types: bool = True) -> Environment:
        templates = build.get_templates(self._module)
        if generate_types:
            types.build_types(templates)
        else:
            types.clear_types()

        return Environment(self._module)
