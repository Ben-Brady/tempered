from __future__ import annotations
import zlib
from pathlib import Path
import typing_extensions as t
from . import module, types
from .template.template import parse_template


class TemperedBase:
    template_files: t.List[Path]

    _module: module.TemperedModule
    _from_string_cache: t.Dict[str, t.Callable[..., str]]
    _generate_types: bool

    def __init__(
        self,
        *,
        template_folder: t.Union[str, Path, None] = None,
        generate_types: bool = True,
    ):
        self._from_string_cache = {}
        self.template_files = []
        self._module = module.TemperedModule()

        self._generate_types = generate_types
        if template_folder:
            self.add_from_folder(template_folder)

    def add_from_file(self, file: t.Union[Path, str]):
        file = Path(file)

        self.template_files.append(file)
        name = str(file)
        html = file.read_text()
        template = parse_template(name, html, file)
        self._module.build_templates([template])
        self._reconstruct_types()

    def add_from_folder(self, folder: t.Union[Path, str]):
        folder = Path(folder)

        FOLDER_PREFIX = f"{folder}/"
        templates = []
        for file in folder.glob("**/*.*"):
            self.template_files.append(file)
            name = str(file)
            name = name[len(FOLDER_PREFIX) :]
            html = file.read_text()
            template = parse_template(name, html, file)
            templates.append(template)

        self._module.build_templates(templates)
        self._reconstruct_types()

    def add_from_string(self, name: str, html: str):
        template = parse_template(name, html, file=None)
        self._module.build_templates([template])
        self._reconstruct_types()

    def add_from_mapping(self, templates: t.Mapping[str, str]):
        template_objs = [
            parse_template(name, html, file=None) for name, html in templates.items()
        ]
        self._module.build_templates(template_objs)
        self._reconstruct_types()

    def render_string(self, html: str, **context: t.Any) -> str:
        if html in self._from_string_cache:
            func = self._from_string_cache[html]
            return func(**context)

        string_hash = hex(zlib.crc32(html.encode()))[2:]
        name = f"string_<{string_hash}>"
        parsed_template = parse_template(name, html)
        self._module.build_templates([parsed_template])
        func = self._module.get_template_func(name)
        self._from_string_cache[html] = func
        return func(**context)

    def render(self, name: str, **context: t.Any) -> str:
        func = self._module.get_template_func(name)
        return func(**context)

    def add_global(self, name: str, value: t.Any):
        self._module.register_global(name, value)

    _has_cleared_types = False

    def _reconstruct_types(self):
        if self._generate_types:
            templates = self._module.get_templates()
            types.build_types(templates)
        elif not self._has_cleared_types:
            self._has_cleared_types = True
            types.clear_types()


class Tempered(TemperedBase):
    template_files: t.List[Path]
    """
    A readonly list of the any files used in templates.

    This is useful for watchdog and code refreshing tools.

    **Example in Flask**

    ```python
    app = Flask()

    if __name__ == "__main__":
        app.run(
            extra_files=tempered.template_files,
            # Flask now reloads when a template changes
        )
    ```
    """

    def __init__(
        self,
        *,
        template_folder: t.Union[str, Path, None] = None,
        generate_types: bool = True,
        **kwargs,
    ):
        """
        Args:
            template_folder: The folder to import templates from, searches recursively
            generate_types: Should type declarations be created for templates? This improves developer experience, however requires IO and can be disabled in production for a small build-time performance boost.
        """
        TemperedBase.__init__(
            self,
            template_folder=template_folder,
            generate_types=generate_types,
        )

    def add_from_file(self, file: t.Union[Path, str]):
        """Add a template from a file.

        Args:
            file: The file to import as the template, the path will be used as it's name.

        **Example**
        ```python
        tempered.add_file("index.html")
        ```
        """
        TemperedBase.add_from_file(self, file)

    def add_from_folder(self, folder: t.Union[Path, str]):
        """Imports templates from a folder

        Transforms all files in a folder into templates, using the file name as the template name.

        Removes the folder prefix from all template names

        Args:
            folder: Imports all files form this folder recursively, the name of the templatse are the filepath without the folder suffix

        **Example**
        ```python
        tempered.add_folder("./additional_templates")
        ```
        """
        TemperedBase.add_from_folder(self, folder)

    def add_from_string(self, name: str, html: str):
        """
        Create a template from a string, specifying the name and contents.

        Args:
            name: The name the templates should have
            html: The template content

        **Example**
        ```python
        tempered.add_string("title.html", \"""
            <h1>{{ title }}</h1>
        \""")
        ```

        """
        TemperedBase.add_from_string(self, name, html)

    def add_from_mapping(self, templates: t.Mapping[str, str]):
        """Add mult

        Useful for adding templates that depend on each other

        Args:
            templates: A dictionary of template names and their content

        **Example**
        ```python
        tempered.add_template_from_string("title.html", \"""
            <h1>
                {{ title }}
            </h1>
        \""")
        """
        TemperedBase.add_from_mapping(self, templates)

    def render(self, name: str, **context: t.Any) -> str:
        """Renders a template using the given parameters

        Args:
            name: The name of the template to render
            context: The parameters to pass to the template

        **Example**
        ```python
        html = tempered.render(
            "user.html",
            name="Ben Brady",
        )
        ```
        """
        return TemperedBase.render(self, name, **context)

    def render_string(self, html: str, **context: t.Any) -> str:
        """
        Render a template from a string, useful for one-off templates.

        Args:
            html: The html of the template to render
            context: The paramemters to pass to the template

        > Note: String template compiles are cached, so it's as fast a regular template

        **Example**

        ```python
        tempered.render_string(
            "<h1> User - {{ name }} </h1>",
            name="Ben Brady",
        )
        ```
        """
        return TemperedBase.render_string(self, html, **context)

    def add_global(self, name: str, value: t.Any):
        """
        Add a global variable to the template context

        Args:
            name: The name the global is assigned to
            value: The value of the global variable

        **Example**

        ```python
        tempered.add_global("DOMAIN", "example.com")
        ```
        """
        TemperedBase.add_global(self, name, value)
