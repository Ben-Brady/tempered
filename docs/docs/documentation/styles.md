## CSS Re

## Scoped Styles

By default, styles are scoped

```html
<button>Hello</button>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap');
button {
    color: #ccc;
    font-size: 16px;
    background: #333;
    padding: .5rem .75rem;
    border-radius: .5rem;
    border: none;
}
</style>
```

Under the hood, a scope class is attached to your css and html. When rendered it will generate something like this:

```html
<button class=" foo-83dcef">Hello</button>
<style>
    @import url("https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap");
    button.foo-83dcef {
        color: #ccc;
        font-size: 16px;
        background: #333;
        padding: .5rem .75rem;
        border-radius: .5rem;
        border: none;
    }
</style>
```

### Global Styles

If you want to opt of scoped styles and make your component's styles global, you can use the `global` attribute

```html
<style global>
  button {
    color: #ccc;
    font-size: 16px;
    background: #333;
    padding: .5rem .75rem;
    border-radius: .5rem;
    border: none;
  }
</style>
```

## Using SaSS/SCSS

Tempered supports

```shell
pip install tempered[sass]
```


You can use scss, using `lang="scss"`

```html
<style lang="scss">
@use "sass:list";
$font-stack: Helvetica, Arial;
body {
  $font-stack: list.append($font-stack, sans-serif);
  font: $font-stack;
}
</style>
```

You can include scss, using `lang="sass"`

```
<style lang="sass">
@use "sass:color"
$primary-color: #333
a
  color: $primary-color
  &:hover
    color: color.scale($primary-color, $lightness: 20%)
</style>
```

- sass/scss
- include_styles

## Omitting styles when rendering

You can omit styles from a template using `include_styles=False`. This is useful for partial renders where you know the styles are already included.

```python
render("foo.html", include_styles=False)
```

