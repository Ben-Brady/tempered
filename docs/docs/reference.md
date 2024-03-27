# Reference

## `Tempered`

### `__init__`

```python
def __init__(self,
    template_folder: str | Path | None = None,
    *,
    generate_types: bool = True,
)
```

### `Tempered.template_files`

A readonly list of the any files used in templates.

This is useful for watchdog and code refreshing tools.

Example in Flask:

```python
app = Flask()

if __name__ == "__main__":
    app.run(
        # Flask will now reload whenever a template changes
        extra_files=tempered.template_files,
    )
```


### `Tempered.add_template()`

```python
def add_template(self, file: Path | str):
```

Creates a template from a file.

```python
tempered.add_template("index.html")

```
### `Tempered.add_template_folder()`

```python
def add_template_folder(self, folder: Path | str):
```

Transforms all files in a folder into templates, using the file name as the template name.

Removes the folder prefix from all template names

### `Tempered.add_template_from_string()`

Create a template from a string, specifying the name and contents.

```python
def add_template_from_string(self,
    name: str,
    **context: t.Any
    ) -> str
```

Example:

```python
tempered.add_template_from_string("title.html", """
    {% param title: str %}
    <h1>
        {{ title }}
    </h1>
""")
```

### `Tempered.render_template()`

```python
def render_template(self,
    name: str,
    **context: t.Any
    ) -> str
```



```python
html = tempered.render_template(
    "user.html",
    name="Ben Brady",
)
```

### `Tempered.render_from_string()`

```python
def render_from_string(self,
    html: str,
    **context: t.Any
    ) -> str
```

::: tempered.Tempered
    options:
        members:
            - add_template
            - add_template_from_folder
            - add_template_from_string
            - render_template
            - render_from_string
            - add_global
            - global_func
            - template_files
