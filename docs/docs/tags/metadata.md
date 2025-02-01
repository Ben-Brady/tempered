```html
<script type="tempered/metadata">
layout: layout.html
parameters:
    user: t.Any
</script>
```

Note: The reason the metadata is in a script tag is so linters and autoformatters don't disdurb it


The metadata tag is the way to define template specific information in tempered.

It's **optional**, but a template should **only have one**  metadata tag

The syntax used for the metadata is [StrictYAML](https://github.com/crdoconnor/strictyaml). This is a stripped down version of YaML, without features like Direct Object Representation and anchors & refs. This limits YaML to just a simple markup format.


## Features

- [Parameters](../documentation/parameters.md)
- [Layouts](../documentation/layout.md)
- [Imports](../documentation/components.md)
- [Style Includes](../documentation/includes.md)

## Exmaples

```html
<script type="tempered/metadata">
layout: layout.html
parameters:
    foo: str
imports:
    foo: bar
style_includes:
    - dynamic.html
</script>
```
