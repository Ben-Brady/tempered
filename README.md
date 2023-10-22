# Tempered (Beta)

Generate native python functions from HTML templates

- Scoped CSS
- Type checked
- Intelisense
- Compiled

[PyPi](https://pypi.org/project/tempered)
[Github](https://github.com/Ben-Brady/tempered)

```python
pip install tempered
```

## Example

```html
<!-- templates/image.html -->
{!param src: str!}
{!param alt: str = ""!}

<img src="{{src}}" alt="{{alt}}">

<style>
    img {
        width: 100px;
        height: 100px;
    }
</style>
```

```python
import tempered

tempered.add_template_folder("./templates")
components = tempered.build()

print(components.image(
    src="/example.png",
    alt="Example Post",
    with_styles=True,
))>
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

## Templating

### Parameters

Use `{!param !}` for parameters, this must placed at the root level
```html
{! param d !}            <!-- Parameter -->
{! param c: list !}      <!-- Typed Parameter-->
{! param b = 2 !}        <!-- Default Value Parameter-->
{! param a: str = "A" !} <!-- Typed Default Value Parameter-->
<!DOCTYPE HTML>
```

### Style Placement

Use `{!styles}` for styles, this is where styles are placed

```html
<head>
    {! styles !}
</head>
```

If omitted, styles are placed at the end of the component

### Style Include

```html
{!include post!}

<head>
    {% styles %}
</head>
```

Manually add a component styles to the HTML, should be placed at the top of the component

This is useful for when you need to include the CSS for dynamically create components, such as with HTMX


### Component

Use `{% component  %}` for a component, call this like

```html
<div>
    {% component post(title=1) %}
</div>
```

### Html

Use `{% html %}` to include literal html without escaping

```html
{!param markdown_html: str}
<div>
    {% html markdown_html %}
</div>
```

### Expressions

Use `{{ VALUE }}` for expressions, these are escaped for parameters and HTML

```html
{! param src: str !}
{! param text: str !}

<a src="{{src}}">
    {{ text }}
</a>
```
**Important**:

### if

Use `{%if %}` and `{% endif %}` for control flow, there are two control flow structures

```html
{!param link: str|None = None}

{% if link %}
    <a href="{{link}}">
        Link
    </a>
{% endif %}
```

You can also have an else block

```html
{!param src: str|None = None}

{% if src %}
    <img src="{{src}}" alt=""/>
{% else %}
    <img src="/images/missing.png" alt=""/>
{% endif %}
```

As well as an elif block

```html
{!param number: int}

{% if number < 10 %}
    {{ number }} is less than 10
{% elif number < 100 %}
    {{ number }} is less than 100
{% else %}
    {{ number }} is bigger than 100
{% endif %}
```

### for

Use `{%for %}`

```html
{!param commments: list[str] !}

{% for comment in comments %}
    <span>
        {{comment}}
    </span>
{% endfor %}
```

```html
{!param commments: list[str] }

<ul>
{% for x in range(10) %}
    <li>{{x}}</li>
{% endfor %}
</ul>
```
