`<script type="tempered/python">` is an escape hatch to include atribtrary python in your templates. It is injected into the template at the place it is used in the tempalte.

```
<script type="tempered/python">
    display_name = f"{user.first_name}, {user.last_name}".title()
</script>

<span>{{ display_name }}</span>
```

would become

```python
display_name = f"{user.first_name}, {user.last_name}".title()
html += f"<span>{ display_name }</span>"
```


It's recommend not to use this for retrieving data or performing actions, as templates do not guarentee the order of execuction or if the code is even run. It's recommended to use it for making data more presentable for use in templates.

## Examples

```html
<script type="tempered/python">
    display_name = f"{user.first_name}, {user.last_name}".title()
</script>

<span>{{ display_name }}</span>
```

```html
<t:for for="post" in="posts">
    <script type="tempered/python">
        created_at = post.createdAt.strftime("%H:%M %d/%-m/%y")
    </script>

    <a class="post">
        <span class="name">{{ post.name }}</span>
        <span class="created">{{ created_at }}</span>
    </a>
</t:for>
```
