# Tempered (Beta)

Convert html templates into native python components


```python
pip install tempered
```

|   |   |   |
| - | - | - |
| [PyPi](https://pypi.org/project/tempered) | [Github](https://github.com/Ben-Brady/tempered) | [Documentation](https://github.com/Ben-Brady/tempered/blob/main/DOCUMENTATION.md) |

## Features

- **Fast**
  - Roughly 3x faster than jinja
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

Output:
```html
<img alt="Example Post" src="/example.png" class=image-83dc><style>img.image-83dc{width:100px;height:100px}</style>
```


## Compiled

Since tempered is runtime compiled and loaded, it provides increase speed compared to jinja. From initial benchmarks, it's roughly 10x faster than jinja2.

Additionally, it allows IDEs to provide intelisense to components


```python
# __components.py
# This file is dynamicly generated when you build the templates
from __future__ import annotations as __annotations
import typing as __typing
from tempered._internals import escape as __escape


def Image(*, src: str, alt: str = '', with_styles: bool = True, **kwargs: __typing.Any) -> str:
    __css = 'img.image-83dc{width:100px;height:100px}'
    __html = f'  <img alt="{__escape(alt)}" src="{__escape(src)}" class=image-83dc>'
    if with_styles and __css:
        __html += '<style>' + (__css + '</style>')
    return __html

```
