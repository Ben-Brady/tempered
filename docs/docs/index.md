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

## Performance

If you want to increase build performance: install `lxml`.

This allows the HTML to parsed much faster and increases build times by 10-30%. However it requires C build tools and is not available on all platforms. If `lxml` installed, Tempered will use it by default.

## Grammar

The formal grammar specified in Extended Backus-Naur Form and can be found [here](https://github.com/Ben-Brady/tempered/blob/main/docs/grammar.ebnf).