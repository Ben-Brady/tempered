from pathlib import Path
import typing_extensions as t
from . import build, parser, types
from .compiler.constants import template_func_name
from .enviroment import Environment, Template

BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _templates: t.List[parser.Template]
    _globals: t.Dict[str, t.Any]
    template_files: t.List[Path]

    def __init__(self, template_folder: t.Union[str, Path, None] = None):
        self.templates_files = []
        self._templates = []
        self._globals = {}
        if template_folder:
            self.add_template_folder(template_folder)

    def add_global(self, name: str, value: t.Any):
        self._globals[name] = value

    def add_template_folder(self, folder: t.Union[Path, str]):
        folder = Path(folder)
        FOLDER_PREFIX = f"{folder}/"
        for file in folder.glob("**/*.*"):
            name = str(file)
            name = name[len(FOLDER_PREFIX) :]
            html = file.read_text()
            template = parser.parse_template(name, html, file)
            self._templates.append(template)

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        name = str(file)
        html = file.read_text()
        template = parser.parse_template(name, html, file)
        self._templates.append(template)

    def add_template_from_string(self, name: str, html: str):
        template = parser.parse_template(name, html, file=None)
        self._templates.append(template)

    def build_enviroment(self, generate_types: bool = True) -> Environment:
        if generate_types:
            types.build_types(self._templates)
        else:
            types.clear_types()

        module = build.build(self._templates, self._globals)
        templates: t.Dict[str, Template] = {}
        for template in self._templates:
            func = module[template_func_name(template.name, template.is_layout)]
            templates[template.name] = Template(func, template)  # type: ignore

        return Environment(templates=templates, globals=self._globals)
