```html
<t:for for="x" in="range(5)">
    {{ x }}
</t:for>
```

The for tags accepts 2 parameters, `for` and `in`, they are both treated as python expressions.

`for` is the target for the loop. e.g. "for **X, Y** in foo"

`in` is the expression to loop over. e.g. "for x in **range(10)**"


## Examples

```html
<ol>
    <t:for for="x" in="range(10)">
        <li>{{ x }}</li>
    </t:for>
</ol>
```

```html
<t:for for="post" in="posts">
    <t:Thumbnail post="post"></t:Thumbnail>
</t:for>
```
