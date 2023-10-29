from . import parser
from .compile.module import compile_module
from .parser import Template
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
    _templates: list[Template]

    def __init__(self):
        self._type_imports = []
        self._templates = []


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


    def add_template_obj(self, template: Template):
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


    def _build_python(self) -> str:
        module_ast = compile_module(
            type_imports=self._type_imports,
            templates=self._templates,
        )
        return ast.unparse(module_ast)

    def build_memory(self) -> ModuleType:
        source = self._build_python()
        spec = spec_from_loader(name="tempered.components", loader=None)
        assert spec is not None
        module = module_from_spec(spec)
        exec(source, module.__dict__)
        return module


    def build_to(self, module: ModuleType):
        source = self._build_python()
        source = autopep8.fix_code(source)
        if not hasattr(module, "__file__") or module.__file__ is None:
            raise ValueError("Module must be loaded from a file")

        with open(module.__file__, "w") as f:
            f.write(source)

        importlib.reload(module)


    def build_static(self):
        try:
            components = self._load_static_file()
        except Exception:
            BUILD_FILE.unlink(missing_ok=True)
            BUILD_FILE.touch()
            components = self._load_static_file()

        self.build_to(components)
        return components


    def _load_static_file(self):
        from tempered.generated import _components
        importlib.reload(_components)
        return _components

