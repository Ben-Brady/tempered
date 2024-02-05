# Tempered

## Adding templates

```python
import components
from tempered import Tempered

tempered = Tempered(
    template_folder="./templates",
) # Initial Creationg

tempered.add_template_folder("./templates")
tempered.add_template("./templates/comment.html")
tempered.add_template_from_string("comment.html", """
    {% param text: str %}
    <span>{{ text }}</span>
""")
```

## Type Generating

By default, tempered will create a dynamic type stubs file alongside the libraries files. This is dynamically updated to fit the currently encoded templates. It enabled IDEs to provide autocomplete on templates names as well as.

However, this may not play well with some IDEs. Additionally, it increases build times and uses IO to write the stubs file, it's recommended to disabled in production.

It can be disabled by adding `generate_types=False` to the Tempered constructor.

```python
Tempered(generate_types=False)
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

If you want to use a component without including it's styles, you can use the `with_styles` parameter to prevent include the CSS. This is useful for when you place components into a page using AJAX/HTMX.

```python
tempered.render_template("partial.html", with_styles=False)
```
#### Sass


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

### Expressions

Use `{{ VALUE }}` for expressions, these are escaped in HTML and parameters

```html
{% param src: str %}
{% param text: str %}

<a src="{{src}}">
    {{ text }}
</a>
```

### Parameters

Use `{% param %}` for parameters

```html
{% param a %}            <!-- Parameter -->
{% param b: list %}      <!-- Typed Parameter-->
{% param c = 2 %}        <!-- Default Value Parameter-->
{% param d: str = "A" %} <!-- Typed Default Value Parameter-->
{% param e: t.Union[str, None] = None %} <!-- Advanced Typing-->
```

> Note: typing_extensions is imported as t and can be used in parameters

### Style Placement

Use `{% styles %}` for styles, this is where styles are placed

```html
<head>
    {% styles %}
</head>
```

If omitted, styles are placed at the end of the component

### Style Include

```html
{% include "post.html" %}

<head>
    {% styles %}
</head>
```

Manually add a component styles to the HTML, should be placed at the top of the component

This is useful for when you need to include the CSS for components that aren't inside the template, such as with HTMX


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

Use `{% component Component() %}` for a component, call this like:

```html
{% import Post from "post.html" %}

<div>
    {% component Post(title="Lorum Ipsum") %}
</div>
```

You have to import components using the import syntax. You can specify any target name.

```html
{% import ANY_NAME from "template_name.html" %}
```

### Set

Use `{% set  %}` to set a variable

```html
<div>
    {% set title = post.title.lower() %}
</div>
```

## Control Flow

### If

Use `{% if %}` and `{% endif %}` for control flow, there are two control flow structures

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
{% param src: str | None = None %}

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

Use `{% for %}`

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
## Performance

### Build Performance

If you want to increase performance, install "lxml". This is not included by default at it's difficult to install on different platforms. Installing this allows the HTML to be parsed much faster, giving you around a 10-30% increase to build time

## Formal Grammar

The formal grammar specified in Extended Backus-Naur Form and can be found [here](https://github.com/Ben-Brady/tempered/blob/main/docs/grammar.ebnf).
