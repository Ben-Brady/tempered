from __future__ import annotations
import zlib
from pathlib import Path
import typing_extensions as t
from . import module, parser, render


class Tempered:
    template_files: t.List[Path]
    static_folder: t.Optional[Path]

    _module: module.TemperedModule
    _from_string_cache: t.Dict[str, t.Callable[..., str]]
    _generate_types: bool

    def __init__(
        self,
        *,
        template_folder: t.Union[str, Path, None] = None,
        static_folder: t.Union[str, Path, None] = None,
        generate_types: bool = True,
    ):
        self._from_string_cache = {}
        self.template_files = []
        self._module = module.TemperedModule()

        self._generate_types = generate_types
        if template_folder:
            self.add_template_folder(template_folder)
        if static_folder:
            self.static_folder = Path(static_folder)

    def add_template(self, file: t.Union[Path, str]):
        file = Path(file)
        self.template_files.append(file)

        name = str(file)
        html = file.read_text()
        template = parser.parse_template(name, html, file)
        self._module.build_templates([template])
        self._reconstruct_types()

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

    def add_template_from_string(self, name: str, html: str):
        template = parser.parse_template(name, html, file=None)
        self._module.build_templates([template])
        self._reconstruct_types()

    def add_templates_from_string(self, templates: t.Mapping[str, str]):
        template_objs = [
            parser.parse_template(name, html, file=None)
            for name, html in templates.items()
        ]
        self._module.build_templates(template_objs)
        self._reconstruct_types()

    def render_from_string(self, html: str, **context: t.Any) -> str:
        if html in self._from_string_cache:
            func = self._from_string_cache[html]
        else:
            string_hash = hex(zlib.crc32(html.encode()))[2:]
            name = f"string_{string_hash}>"
            parsed_template = parser.parse_template(name, html)
            self._module.build_templates([parsed_template])
            func = self._module.get_template_func(name)
            self._from_string_cache[html] = func

        return func(**context)

    def render_template(self, name: str, **context: t.Any) -> str:
        func = self._module.get_template_func(name)
        return func(**context)

    def add_global(self, name: str, value: t.Any):
        self._module.register_global(name, value)

    TFunc = t.TypeVar("TFunc", bound=t.Callable)

    def global_func(self, func: TFunc) -> TFunc:
        self._module.register_global(func.__name__, func)
        return func

    _are_typed_deleted = False

    def _reconstruct_types(self):
        if not self._generate_types:
            if not self._are_typed_deleted:
                self._are_typed_deleted = True
                render.clear_types()
        else:
            templates = self._module.get_templates()
            render.build_types(templates)


class TemperedInterface(Tempered):
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

    static_folder: t.Optional[Path]
    "The static folder, if any"

    def __init__(
        self,
        *,
        template_folder: t.Union[str, Path, None] = None,
        static_folder: t.Union[str, Path, None] = None,
        generate_types: bool = True,
    ):
        """
        Args:
            template_folder: The folder to import templates from, searches recursively
            static_folder: The folder to import static assets from, searches recursively
            generate_types: Should type declarations be created for templates? This improves developer experience, however requires IO and can be disabled in production for a small build-time performance boost.
        """
        Tempered.__init__(
            self,
            template_folder=template_folder,
            static_folder=static_folder,
            generate_types=generate_types,
        )

    def add_template(self, file: t.Union[Path, str]):
        """Add a template from a file.

        **Example**
        ```python
        tempered.add_template("index.html")
        ```

        Args:
            file: The file to import as the template, the path will be used as it's name.
        """
        Tempered.add_template(self, file)

    def add_template_folder(self, folder: t.Union[Path, str]):
        """Imports templates from a folder

        Transforms all files in a folder into templates, using the file name as the template name.

        Removes the folder prefix from all template names

        Args:
            folder: Imports all files form this folder recursively, the name of the templatse are the filepath without the folder suffix
        """
        Tempered.add_template_folder(self, folder)

    def add_template_from_string(self, name: str, html: str):
        """Create a template from a string, specifying the name and contents.

        **Example**
        ```python
        tempered.add_template_from_string("title.html", \"""
            {% param title: str %}
            <h1>
                {{ title }}
            </h1>
        \""")
        ```

        Args:
            name: The name the templates hould have
            html: The template content
        """
        Tempered.add_template_from_string(self, name, html)

    def add_templates_from_string(self, templates: t.Mapping[str, str]):
        """Add

        Useful for adding templates that depend on each other

        Args:
            templates: A dictionary of template names and their content
        """
        Tempered.add_templates_from_string(self, templates)

    def render_template(self, name: str, **context: t.Any) -> str:
        """Renders a template using the given parameters

        **Example**
        ```python
        html = tempered.render_template(
            "user.html",
            name="Ben Brady",
        )
        ```

        Args:
            name: The name of the template to render
            context: The parameters to pass to the template
        """
        return Tempered.render_template(self, name, **context)

    def render_from_string(self, html: str, **context: t.Any) -> str:
        """
        Render a template from a string, useful for one-off templates.

        **String templates are cached**

        Args:
            html: The html of the template to render
            context: The paramemters to pass to the template
        """
        return Tempered.render_from_string(self, html, **context)

    def add_global(self, name: str, value: t.Any):
        """
        Add a global variable to the template context

        **Example**

        ```python
        tempered.add_global("DOMAIN", "example.com")
        ```

        Args:
            name: The name the global is assigned to
            value: The value of the global variable
        """
        Tempered.add_global(self, name, value)


    TFunc = t.TypeVar("TFunc", bound=t.Callable)
    def global_func(self, func: TFunc) -> TFunc:
        """A decorator to insert a function into the templating context

        **Example**

        ```python
        @tempered.global_func
        def format_as_ddmmyyyy(date: datetime):
            return date.strftime("%d/%m/%Y")
        ```

        ```html
        <span>
            {{ format_as_ddmmyyyy(user.created_at) }}
        </span>
        ```
        """
        return Tempered.global_func(self, func)

