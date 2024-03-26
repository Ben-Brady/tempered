# Examples

## Even and Odd Table
```html
<!DOCTYPE html>
<html>
<body>
    <div class="table">
    {% for x in range(10) %}
        {% if x % 2 == 0 %}
            <div class="row even">
                {{x}}
            </div>
        {% else %}
            <div class="row odd">
                {{x}}
            </div>
        {% endif %}
    {% endfor %}
</div>
</body>

<style>
    .table {
        width: 500px;
        height: fit-content;
        border: solid black 1px;

        display: flex;
        flex-flow: column nowrap;
    }

    .row {
        width: 100%;
        color: black;
        text-align: center;
    }
    .row.even { background: #FAFAFF; }
    .row.odd { background: #DADDD8; }
</style>
</html>
```

<html class="string_bb5fbcfe>-83dcef"><body class="string_bb5fbcfe>-83dcef"><div class="table string_bb5fbcfe>-83dcef">  <div class="row even string_bb5fbcfe>-83dcef">0</div>    <div class="row odd string_bb5fbcfe>-83dcef">1</div>    <div class="row even string_bb5fbcfe>-83dcef">2</div>    <div class="row odd string_bb5fbcfe>-83dcef">3</div>    <div class="row even string_bb5fbcfe>-83dcef">4</div>    <div class="row odd string_bb5fbcfe>-83dcef">5</div>    <div class="row even string_bb5fbcfe>-83dcef">6</div>    <div class="row odd string_bb5fbcfe>-83dcef">7</div>    <div class="row even string_bb5fbcfe>-83dcef">8</div>    <div class="row odd string_bb5fbcfe>-83dcef">9</div>  </div><style>.table.string_bb5fbcfe\>-83dcef{width:500px;height:fit-content;border:solid black 1px;display:flex;flex-flow:column nowrap}.row.string_bb5fbcfe\>-83dcef{width:100%;color:black;text-align:center}.row.string_bb5fbcfe\>-83dcef.even.string_bb5fbcfe\>-83dcef{background:#FAFAFF}.row.string_bb5fbcfe\>-83dcef.odd.string_bb5fbcfe\>-83dcef{background:#DADDD8}</style>
