# Configuration

## Type Generating

By default, tempered will create a dynamic type stubs file alongside the libraries files. This is dynamically updated to fit the currently encoded templates. It enabled IDEs to provide autocomplete on templates names as well as.

However, this may not play well with some IDEs. Additionally, it increases build times and uses IO to write the stubs file, it's recommended to disabled in production. It can be disabled by adding `generate_types=False` to the Tempered constructor.

```python
Tempered(generate_types=False)
```

## Performance

If you want to increase build performance: install `lxml`.

This allows the HTML to parsed much faster and increases build times by 10-30%. However it is not available on all platforms, so you. If `lxml` installed, Tempered will use it by default.
