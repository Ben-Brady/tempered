<p align="center">
    <img
        height=128
        src="https://github.com/Ben-Brady/tempered/assets/64110708/c30f75f4-ab69-48a8-b595-fec5ad9baa38"
        alt="Tempered Banner"
    >
</p>

<p align="center">
    <em>A modern html templating library for python</em>
</p>

---

Documentation: https://github.com/Ben-Brady/tempered/blob/main/docs/index.md

Source Code: https://github.com/Ben-Brady/tempered


```python
pip install tempered
```

Tempered is templating library designed around HTML and type safety.

- **Fast**: Sub-millisecond render times.
- **Scoped and Bundled CSS**: CSS is scoped per file and then bundled together into a single stylesheet per page
- **Native Preprocesser Support**: Native support for Sass
- **Component Based**: Each template is a components and can call other components
- **Layouts**: Templates can use layouts, based on jinja2's implementation
- **Dynamically Typed**: Optional dynamic type information can be built with components for better intelisense.


## Lightning Fast

- Templates are optimised and compiled into Python leading to microsecond long render times.
- 5x faster than Jinja, 50x faster the django

<a href="https://github.com/Ben-Brady/tempered/tree/main/benchmarks">
<picture align="center">
  <img align="center" alt="Full Page Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/684ff121-a2c9-41df-94dd-f5c0aa136d3e">
</picture>
<picture align="center">
  <img align="center" alt="Partials Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/6bbc6c1d-107b-47b3-9b59-fb9c78e6352f">
</picture>
<picture>
  <img align="center" alt="Static Page Benchmark" src="https://github.com/Ben-Brady/tempered/assets/64110708/a9c3242c-872d-4969-878d-fb39547ca67a">
</picture>
</a>

---

## Native CSS

CSS is scoped per componenet and bundled together into a single stylesheet.

```html
<div>
  <img src="https://picsum.photos/320/180" alt="Example Post">
</div>

<style lang="sass">
  div {
    box-sizing: content-box;
    width: fit-content;
    overflow: hidden;

    border-radius: 1rem;
    border: .15rem solid black;

    img {
      height: auto;
      width: 10rem;
    }
  }
</style>
```

--

##

---

## Example

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
