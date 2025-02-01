Documenting parameters are optional, if a parameter insn't specified it will still be resovled from the kwargs.

However, it allows temepred to type hint the parameters a template uses so it can be shown when calling `render`.
This means you can get typing on your template calls.

## Specifying types

You can specify the types on a parameter and these will be used for typegen when calling templates.

Note: typing_extensions is automatically imported as t

```html
<script type="tempered/metadata">
    parameters:
        - foo: str
        - bar: t.Any
</script>
```

## Default Values

If you want to specify a default value, you can do so

```html
<script type="tempered/metadata">
    parameters:
        - foo: str
        - bar: str
</script>
```

Note: This syntax isn't nice to work with, so may be changed in the near future
