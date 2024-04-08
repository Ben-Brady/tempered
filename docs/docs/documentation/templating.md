# Templates

Tempered templates are based on Jinja with several modifications.

```html
{% layout "layout.html" %}
{% param text: str %}
<div>
    {text}
</div>
```

## Layouts

## Slots and Blocks

A slot is a hole, and a block is a plug to fill that hole.

```html
<!-- layout.html -->
<title>
    Tempered /
    {% block title %}Default Title{% endblock %}
</title>
```

## Tags

### Expressions

Use `{{ EXPR }}` for expressions,

```html
<span>{{ text }}</span>
```

These are escaped in HTML and tag parameters, so they are protected against XSS

```html
<a src="{{src}}"> <!-- This is safe -->
    {{ text }}  <!-- And so is this -->
</a>
```

> Important: Ensure you surround attributes in quotes `"` to prevent XSS
> `<a href="{{src}}"/>` is safe
> `<a href={{src}}/>` is unsafe

### if

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

### for

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

### html

Use `{% html %}` to include literal html without escaping

```html
{%param markdown_html: str %}
<div>
    {% html markdown_html %}
</div>
```

### param

Use `{% param %}` for parameters

```html
{% param a %}
{% param b: list %}
{% param c = 2 %}
{% param d: str = "A" %}
{% param e: t.Optional[str, None] = None %} <!-- Advanced Typing-->
```
> Note: typing_extensions is imported as t and can be used in parameters

### component

Use `{% component Component() %}` for a component, call this like:

```html
{% import Post from "post.html" %}

<div>
    {% component Post(title="Lorum Ipsum") %}
</div>
```

### import

You have to import components using the import syntax. You can specify any target name.

```html
{% import ANY_NAME from "template_name.html" %}
```

### set

Use `{% set %}` to set a variable

```html
<div>
    {% set title = post.title.lower() %}
</div>
```


### styles

Use `{% styles %}` for styles, this is where styles are placed

```html
<head>
    {% styles %}
</head>
```

If omitted, styles are placed at the end of the component

### include

You can manually include a seperate components styles using `include`, should be placed at the top of the component. This treats the target component as a depedency.

```html
{% include "post.html" %}

<head>
    {% styles %}
</head>
```

You shouldn't have to do this normally, only if your dynamically adding a component through javascript such as with HTMX.

## Styles

Anything placed in style tags is transformed into the componenets CSS.
```html
<div>
    Hello
</div>
<style>
    div {
        height: 10rem;
        width: 10rem;
        text-align: center;
        justify-text: center;
    }
</style>
```

### Scoping

Style tags are automatically converted into CSS, By default css is scoped per component, this means you don't have to worry CSS name collisions. This is done by applying a component specific class to each

Watch you, you cannot place dynamic attributes in the CSS, this is becuase CSS is shared per component

### Global

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

### `with_styles`

If you want to use a component without including it's styles, you can use the `with_styles` parameter to prevent include the CSS. This is useful for when you place components into a page using AJAX/HTMX.

```python
tempered.render_template("partial.html", with_styles=False)
```
### Sass

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

