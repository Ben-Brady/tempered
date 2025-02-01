```html
<t:if condition="showButton">
    <button>Click Me</button>
</t:if>
```

`t:if` lets you render HTML conditionally.

The `condition` parameter is evaluated as python code and if true, the HTML is rendered.

## Elif and Else

You can also use `t:elif` and `t:else` with a `t:if` tag. These should be place adject to the t:if tag, not nested.

```html
<t:if condition="True">
    Foo
</t:if>
<t:elif condition="False">
    Bar
</t:elif>
<t:else>
    Far
</t:else>
```

It's invalid to put anything inbetween these tags

```html
<t:if>
</t:if>
INBETWEEN
<t:else>
</t:else>
```

## Examples

```html
<t:if condition="user != None">
    {{ user.name }}
</t:if>
<t:else>
    Anonymous
</t:else>
```

```html
<ul>
    <t:for for="x" in="range(100)">
        <li>
            <t:if condition="x % 3 == 0 and x % 5 == 0">
                FizzBuzz
            </t:if>
            <t:elif condition="x % 3 == 0">
                Fizz
            </t:elif>
            <t:elif condition="x % 5 == 0">
                Buzz
            </t:elif>
            <t:else>
                {{ x }}
            </t:else>
        </li>
    </t:for>
</ul>
```
