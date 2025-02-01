# Configuration

## Type Generating

By default, tempered will create a dynamic type stubs file alongside the libraries files. This is dynamically updated to fit the currently encoded templates. It enabled IDEs to provide autocomplete on templates names as well as.

However, this may not play well with some IDEs. Additionally, it increases build times and uses IO to write the stubs file, it's recommended to disabled in production. It can be disabled by adding `generate_types=False` to the Tempered constructor.

```python
Tempered(generate_types=False)
```
