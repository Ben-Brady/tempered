# Tempered (Beta)

Convert html templates into native python components

[PyPi](https://pypi.org/project/tempered)
[Github](https://github.com/Ben-Brady/tempered)
[Documentation](https://github.com/Ben-Brady/tempered/blob/main/DOCUMENTATION.md)

```python
pip install tempered
```

## Features

- **Scoped CSS**
  - CSS is scoped per component
- **Components**
  - Each template is it's own components and can call other components
- **Layouts**
  - Templates can inherit layouts, based on jinja2's implementation
- **Codegen**
  - The native python out has the choice between being built in memeory or to a static file
- **Type Checked**
  - The compiled components can be checked by static analysers such as mypy
- **Intelisense**
  - Components have intelisense support
- **HTMX Support**
  - Designed to used with HTMX

## Example

```html
<!-- templates/Image.html -->
{% param src: str %}
{% param alt: str = "" %}

<img src="{{src}}" alt="{{alt}}">

<style>
    img {
        width: 100px;
        height: 100px;
    }
</style>
```

```python
from tempered import Tempered

tempered = Tempered()
tempered.add_template_folder("./templates")
components = tempered.build()

print(components.Image(
    src="/example.png",
    alt="Example Post",
))
```

```html
<!-- Generated -->
<style>img.tempered-1ad5be0d {width: 100px;height: 100px;}</style>
<img class='tempered-1ad5be0d' src="/example.png" alt="Example Post">
```


## Compiled

Since tempered is runtime compiled and loaded, it provides increase speed compared to jinja. From initial benchmarks, it's roughly 10x faster than jinja2.

Additionally, it allows IDEs to provide intelisense to components


```python
# __components.py
# This file is dynamicly generated when you build the templates
from tempered import _internals  as __internals

IMAGE_STYLE = "<style>img.tempered-1ad5be0d {width: 100px;height: 100px;}</style>"

def image(*, src: str, alt: str = "", with_styles: bool = True) -> str:
    __html = ""
    if with_styles:
        __html += IMAGE_STYLE
    __html += "<img class='tempered-1ad5be0d' src=\""
    __html += __internals.escape(src)
    __html += "\" alt=\""
    __html += __internals.escape(alt)
    __html += "\">"
    return __html
```
