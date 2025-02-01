```
{{ x }}
```

This is a way to include a python expression in a template

It's only valid in the text section of HTML or in attributes.

It's not valid inside `t:` tags, as these are either treated as python expressions or just raw values. This means `<t:if condition="{{ x }}">` is invalid, do `<t:if condition="x">` instead.


```html
{{ 1 + 2 }} = 3
```
