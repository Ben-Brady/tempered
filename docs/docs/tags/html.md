t:html is an escape hatch for include raw HTML in a template.

Note: This should not be used commonly and should not include any user provided data. This is specificly designed for library created html, such as from syntax highlighting or markdown translation.

```html
<t:html value="<h1>This is RAW!!!!</h1>">
```

```html
<script type="tempered/metadata">
parameters:
    codeHtml: str
</script>

<code><pre>
    <t:html value="codeHtml">
</pre>
</code>
