
# Templating Documentation

## Parameters

Use `{!param !}` for parameters
```html
{! param d !}            <!-- Parameter -->
{! param c: list !}      <!-- Typed Parameter-->
{! param b = 2 !}        <!-- Default Value Parameter-->
{! param a: str = "A" !} <!-- Typed Default Value Parameter-->
```

## Styles

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
    {! styles !}
</head>
```

Manually add a component styles to the HTML, should be placed at the top of the component

This is useful for when you need to include the CSS for dynamically create components, such as with HTMX


## Values

### Escaped Expressions

Use `{{ VALUE }}` for expressions, these are escaped for parameters and HTML

```html
{! param src: str !}
{! param text: str !}

<a src="{{src}}">
    {{ text }}
</a>
```

### Raw HTML

Use `{% html %}` to include literal html without escaping

```html
{!param markdown_html: str}
<div>
    {% html markdown_html %}
</div>
```

### Component

Use `{% component  %}` for a component, call this like

```html
<div>
    {% component post(title=1) %}
</div>
```
**Important**
> Ensure you surround attributes in \"\" to prevent XSS, e.g. `<a href="{{src}}"/>`

## Control Flow

### If

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

### For

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
