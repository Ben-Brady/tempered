from . import parser, build
from .compile.module import compile_module
import ast
import inspect
import importlib
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import LiteralString, Any, cast, Literal, overload
import autopep8


BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _type_imports: list[ast.ImportFrom]
    _templates: list[parser.Template]

    def __init__(self, template_folder: str|Path|None = None):
        self._type_imports = []
        self._templates = []
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
            self.add_template(
                name=name,
                template=template,
                context=context
            )


    def add_template(self,
            name: str,
            template: LiteralString,
            context: dict[str, Any] = {}
            ):
        template_obj = parser.parse_template(name, template, context)
        self._templates.append(template_obj)


    def add_template_obj(self, template: parser.Template):
        self._templates.append(template)


    def register_type(self, type: type):
        filepath = inspect.getfile(type)
        module = inspect.getmodulename(filepath)
        name = type.__name__
        import_ = ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name)],
            level=0,
        )
        self._type_imports.append(import_)


    def build_to(self, module: ModuleType):
        build.build_to(module, self._type_imports, self._templates)


    def build_memory(self) -> ModuleType:
        return build.build_memory(self._type_imports, self._templates)


    def build_static(self):
        return build.build_static(self._type_imports, self._templates)
