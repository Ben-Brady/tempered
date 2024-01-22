# Tempered (Beta)

Convert html templates into native python components

```python
pip install tempered
```

| [Documentation](https://github.com/Ben-Brady/tempered/blob/main/docs/index.md) | [PyPi](https://pypi.org/project/tempered) | [Github](https://github.com/Ben-Brady/tempered)|
| - | - | - |

## Features

- **Fast**
  - Roughly 5x faster than jinja, 50x faster than django
- **Scoped CSS**
  - CSS is scoped per component
- **Component Based**
  - Each template is a components and can call other components
- **Layouts**
  - Templates can use layouts, based on jinja2's implementation
- **Intelisense**
  - Components have dynamically created type information providing intelisense support
- **Type Checked**
  - Static builds can be checked by static analysers such as mypy

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

components = Tempered("./templates").build()

print(components.Image(
    src="/example.png",
    alt="Example Post",
))
```

```html
<img alt="Example Post" src=/example.png class=image-83dc><style>img.image-83dc{width:100px;height:100px}</style>
```

## Transpiled

Templates are transpiled inmto python functions, this provides increased performance.

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
