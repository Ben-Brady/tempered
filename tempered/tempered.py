from . import parser, build
from pathlib import Path
from types import ModuleType
import typing_extensions as t


BUILD_FILE = Path(__file__).parent.joinpath("generated/__components.py")


class Tempered:
    _templates: t.List[parser.Template]
    template_files: t.List[Path]


    def __init__(self, template_folder: t.Union[str, Path, None] = None):
        self._templates = []
        self.template_files = []
        if template_folder:
            self.add_template_folder(template_folder)



    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        name = file.stem
        template = file.read_text()
        template_obj = parser.parse_template(
            name,
            template,
            file=file,
        )
        self._templates.append(template_obj)
        self.template_files.append(file)


    def add_template_folder(self, folder: t.Union[Path, str]):
        for file in Path(folder).glob("**/*.*"):
            self.add_template(file)


    def add_template_from_string(self, name: str, template: str):
        template_obj = parser.parse_template(name, template)
        self._templates.append(template_obj)


    def add_template_obj(self, template: parser.Template):
        self._templates.append(template)


    def build_to(self, module: ModuleType) -> None:
        build.build_to(module, self._templates)


    def build_memory(self) -> ModuleType:
        return build.build_memory(self._templates)

    def build_static(self):
        return build.build_static(self._templates)

