from . import parser, build
from .compile.module import compile_module
import ast
import inspect
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from types import ModuleType
from typing_extensions import LiteralString, Any, cast, overload


BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _templates: list[parser.Template]
    template_files: list[Path]


    def __init__(self, template_folder: str|Path|None = None):
        self._templates = []
        self.template_files = []
        if template_folder:
            self.add_template_folder(template_folder)


    def add_template_folder(self,
            folder: Path|str,
            context: dict[str, Any] = {}
            ):
        folder = Path(folder)
        for file in folder.glob("**/*.*"):
            name = file.stem
            template = cast(LiteralString, file.read_text())
            template_obj = parser.parse_template(
                name,
                template,
                filepath=file,
                context=context,
            )
            self.template_files.append(file)
            self._templates.append(template_obj)


    def add_template(self,
            file: Path|str,
            context: dict[str, Any] = {}
            ):
        file = Path(file)
        name = file.stem
        template = cast(LiteralString, file.read_text())
        template_obj = parser.parse_template(
            name,
            template,
            filepath=file,
            context=context,
        )
        self._templates.append(template_obj)
        self.template_files.append(file)


    def add_template_from_string(self,
            name: str,
            template: LiteralString,
            context: dict[str, Any] = {}
            ):
        template_obj = parser.parse_template(name, template, context=context)
        self._templates.append(template_obj)


    def add_template_obj(self, template: parser.Template):
        self._templates.append(template)


    def build_to(self, module: ModuleType) -> None:
        build.build_to(module, self._templates)


    def build_memory(self) -> ModuleType:
        return build.build_memory(self._templates)

    def build_static(self):
        return build.build_static(self._templates)
