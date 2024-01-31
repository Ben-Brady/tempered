# Tempered (Beta)


A modern html templating library for python

| [Documentation](https://github.com/Ben-Brady/tempered/blob/main/docs/index.md) | [PyPi](https://pypi.org/project/tempered) | [Github](https://github.com/Ben-Brady/tempered)|
| - | - | - |

```python
pip install tempered
```

## Features

- **Fast**: Sub-millisecond render times. Roughly 5x faster than jinja, 50x faster than django
- **Scoped and Bundled CSS**: CSS is scoped per file and then bundled together into a single stylesheet per page
- **Native Preprocesser Support**: Native support for Sass and Typescript
- **Component Based**: Each template is a components and can call other components
- **Layouts**: Templates can use layouts, based on jinja2's implementation
- **Dyanimcly Typed**: Optional dynamic type information can be built with components for better intelisense.

```python
from tempered import Tempered

tempered = Tempered("./templates")
html = tempered.render_template("image.html",
    src="/example.png",
    alt="Example Post",
)
print(html)
```

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

```html
<img alt="Example Post" src="/example.png" class=image-83dc><style>img.image-83dc{width:100px;height:100px}</style>
```

## Transpiled

Templates are transpiled into python functions to provide increased performance.

<picture align="center">
  <img align="center" alt="Full Page Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/684ff121-a2c9-41df-94dd-f5c0aa136d3e">
</picture>
<picture align="center">
  <img align="center" alt="Partials Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/6bbc6c1d-107b-47b3-9b59-fb9c78e6352f">
</picture>
<picture>
  <img align="center" alt="Static Page Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/a9c3242c-872d-4969-878d-fb39547ca67a">
</picture>

[View Benchmarks Here](https://github.com/Ben-Brady/tempered/tree/main/benchmarks)

## Type Hinted

Dynamically created type information allows improved IDE intergration.

[Type Hinting.webm](https://github.com/Ben-Brady/tempered/assets/64110708/35fd09f1-b7ab-47e0-802a-6fb3e0dbb6e9)

