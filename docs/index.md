# Tempered

## Adding templates

```python
import components
from tempered import Tempered

tempered = Tempered()

tempered.add_template("./templates/comment.html")
tempered.add_template_folder("./templates")
tempered.add_template_from_string("TEMPLATE_NAME", """
    TEMPLATE_CONTENTS
""")
```

## Building

Tempered offers several ways to build your templates, you can either:

- Build in memory
- Build to a static file
- Build to a module

### build_memory

Building in memory provides the simplist build system, however it provides no-intelisense. It runs the python coded through exec and transforms it into a module.

### build_static

Building staticly saves the generated templates to a file inside the tempered folder, this means that the code can recieve intelisense and type checking. However, this relies on rather weak type inferance and doesn't work sometimes.

### build_to

Build module allows you have a local file built into. This provides the strongest guarentee of type saftey as a local file is always type checked.

Additionally when building into this module, tempered will override the import cache meaning that this update will apply even if you've already imported

```python
# components.py
# EMPTY
```

```python
import components
from tempered import Tempered

tempered = Tempered()
tempered.add_template_from_string("Comment", """
    {% param author: str %}
    {% param text: str %}
    <div>
        <h2>{{ author }}</h2>
        <p>{{ text }}</p>
    </div>
""")

tempered.build_to(components)
print(components.Comment(
    author="Ben Brady",
    text="This library is pretty goated"
))
```

```python
# components.py AFTER
from __future__ import annotations as __annotations
import typing as __typing
from tempered._internals import escape as __escape


def Comment(*, author: str, text: str, with_styles: bool = True, **kwargs: __typing.Any) -> str:
    return f'  <div><h2>{__escape(author)}</h2><p>{__escape(text)}</div>'

```

## Templates

### Styles

#### Scoping

Style tags are automatically converted into CSS, By default css is scoped per component, this means you don't have to worry CSS name collisions. This is done by applying a component specific class to each

Watch you, you cannot place dynamic attributes in the CSS, this is becuase CSS is shared per component

#### Global

If you want to disable CSS scoping, you can place a global attribute on your style tag.

```html
<style global>
    html {
        --text: #262626;
        --background: #ededed;
        --primary: #91c0c0;
        --secondary: #d5d5e7;
        --accent: #579898;
        --error: #FD2929;
    }
</style>
```

#### `with_styles`

If you want to use a component without including it's styles, you can use the `with_styles` parameter to prevent include the CSS. This is useful for when you place components into a page using javascript or HTMX.

#### Scss

If you want to use sass, you can declare it on a style tag with `lang="scss"` or `lang="sass"` to get sass or scss respectively

```html
<style lang="scss">
    a {
        b {
            color: red;
        }
    }
</style>

<style lang="sass">
    a
        b
            color: red
</style>
```

`a b {color: red;}`

## Template Tags

### Parameters

Use `{%param %}` for parameters

```html
{% param a %}            <!-- Parameter -->
{% param b: list %}      <!-- Typed Parameter-->
{% param c = 2 %}        <!-- Default Value Parameter-->
{% param d: str = "A" %} <!-- Typed Default Value Parameter-->
{% param e: t.Union[str, None] = None %} <!-- Advanced Typing-->
```

> Note: typing_extensions is imported as t and can be used in parameters

### Style Placement

Use `{%styles}` for styles, this is where styles are placed

```html
<head>
    {% styles %}
</head>
```

If omitted, styles are placed at the end of the component

### Style Include

```html
{%include "post.html" %}

<head>
    {% styles %}
</head>
```

Manually add a component styles to the HTML, should be placed at the top of the component

This is useful for when you need to include the CSS for components that aren't inside the template, such as with HTMX

### Expressions

Use `{{ VALUE }}` for expressions, these are escaped for parameters and HTML

```html
{% param src: str %}
{% param text: str %}

<a src="{{src}}">
    {{ text }}
</a>
```

> Important: Ensure you surround attributes in \"\" to prevent XSS, e.g. `<a href="{{src}}"/>` vs `<a href={{src}}/>`

### Raw HTML

Use `{% html %}` to include literal html without escaping

```html
{%param markdown_html: str %}
<div>
    {% html markdown_html %}
</div>
```

### Component / Import

Use `{<Component()>}` for a component, call this like:

```html
{% import Post from "post.html" %}

<div>
    {<Post(title="Lorum Ipsum")>}
</div>
```

You have to import components using the import syntax. You can specify any target name.

```html
{% import ANY_NAME from "template_name.html" %}
```

### Set

Use `{% set  %}` to set a variable

```html
{% param post %}
<div>
    {% set title = post.title.lower() %}
</div>
```

This can also be paired with control flow

## Control Flow

### If

Use `{%if %}` and `{% endif %}` for control flow, there are two control flow structures

```html
{% param link: str | None = None %}

{% if link %}
    <a href="{{link}}">
        Link
    </a>
{% endif %}
```

You can also have an else block

```html
{% param src: str|None = None %}

{% if src %}
    <img src="{{src}}" alt=""/>
{% else %}
    <img src="/images/missing.png" alt=""/>
{% endif %}
```

As well as elif blocks

```html
{% param number: int %}

<span>
    {% if number < 10 %}
        {{ number }} is less than 10
    {% elif number < 100 %}
        {{ number }} is less than 100
    {% elif number < 1000 %}
        {{ number }} is less than 1000
    {% else %}
        {{ number }} is bigger than 1000
    {% endif %}
</span>
```

### For

Use `{%for %}`

```html
{% param commments: list[str] %}

{% for comment in comments %}
    <span>
        {{ comment }}
    </span>
{% endfor %}
```

```html
{%param commments: list[str] }

<ul>
{% for x in range(10) %}
    <li>{{x}}</li>
{% endfor %}
</ul>
```

## Examples

```html
<div class="table">
    {% for x in range(10) %}
        {% if x % 2 == 0 %}
            <div class="row even">
                {{x}}
            </div>
        {% else %}
            <div class="row odd">
                {{x}}
            </div>
        {% endif %}
    {% endfor %}
</div>

<style>
    .table {
        width: 500px;
        height: fit-content;
        border: solid black 1px;

        display: flex;
        flex-flow: column nowrap;
    }

    .row {
        width: 100%;
        color: black;
        text-align: center;
    }
    .row.even { background: #FAFAFF; }
    .row.odd { background: #DADDD8; }
</style>
```

## Formal Grammar

The formal grammar specified in Extended Backus-Naur Form and can be found [here](https://github.com/Ben-Brady/tempered/blob/main/docs/grammar.ebnf).
