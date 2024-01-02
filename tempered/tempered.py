from . import parser, build, types
from .enviroment import Template, Environment
from .compiler.utils import component_func_name
from pathlib import Path
from types import ModuleType
import typing_extensions as t
from dataclasses import dataclass

BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


@dataclass
class TemplateInfo:
    name: str
    body: str
    file: t.Optional[Path]

    def parse(self) -> parser.Template:
        return parser.parse_template(self.name, self.body, self.file)


class Tempered:
    _templates: t.List[TemplateInfo]
    _globals: t.Dict[str, t.Any]

    def __init__(self, template_folder: t.Union[str, Path, None] = None):
        self._templates = []
        self._globals = {}
        if template_folder:
            self.add_template_folder(template_folder)

    @property
    def template_files(self) -> t.List[Path]:
        return [
            template.file for template in self._templates if template.file is not None
        ]

    def add_global(self, name: str, value: t.Any):
        self._globals[name] = value

    def add_template_folder(self, folder: t.Union[Path, str]):
        for file in Path(folder).glob("**/*.*"):
            self.add_template(file)

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        name = file.stem
        body = file.read_text()
        template_info = TemplateInfo(
            name=name,
            body=body,
            file=file,
        )
        self._templates.append(template_info)

    def add_template_from_string(self, name: str, template: str):
        template_info = TemplateInfo(
            name=name,
            body=template,
            file=None,
        )
        self._templates.append(template_info)

    def _parse_templates(self) -> t.List[parser.Template]:
        return [template.parse() for template in self._templates]

    def build_to(self, module: ModuleType) -> None:
        build.build_to(module, self._parse_templates(), self._globals)

    def build_memory(self) -> ModuleType:
        return build.build_memory(self._parse_templates(), self._globals)

    def build_static(self):
        return build.build_static(self._parse_templates(), self._globals)

    def build_enviroment(self, generate_types: bool = True) -> Environment:
        template_objs = self._parse_templates()
        m = build.build_memory(template_objs, self._globals)
        if generate_types:
            types.build_types(template_objs)
        else:
            types.clear_types()

        templates: t.Dict[str, Template] = {}
        for template in template_objs:
            if template.is_layout:
                continue

            func = getattr(m, component_func_name(template.name))
            templates[template.name] = Template(func,self. _globals)  # type: ignore

        return Environment(templates=templates, globals={})
