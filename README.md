# Tempered (Beta)

Convert html templates into native python components

```python
pip install tempered
```

| [Documentation](https://github.com/Ben-Brady/tempered/blob/main/Documentation.md) | [PyPi](https://pypi.org/project/tempered) | [Github](https://github.com/Ben-Brady/tempered)|
| - | - | - |

## Features

- **Fast**
  - Roughly 5x faster than jinja, 50x faster than django
- **Scoped CSS**
  - CSS is scoped per component
- **Components**
  - Each template is it's own components and can call other components
- **Layouts**
  - Templates can inherit layouts, based on jinja2's implementation
- **Type Checked**
  - The compiled components can be checked by static analysers such as mypy
- **Intelisense**
  - Components have intelisense support

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
<img alt="Example Post" src=/example.png class=image-83dc><style>img.image-83dc{width:100px;height:100px}</style>
```

## Compiled

<img
  src="https://github.com/Ben-Brady/tempered/assets/64110708/456540e2-cdeb-4ebb-a6f5-c2f82b33f499"
  alt="Benchmarks"
  width="240" height="270"
  align="center"
>

Tempered is runtime compiled and loaded, this provides increased performance as well as intelisense and type checking.

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
