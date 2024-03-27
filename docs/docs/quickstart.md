# Quickstart

## Basic Setup

### Step 1

```
pip install tempered
```


### Create your First Template

```html
<!-- templates/title.html -->
<h1>
    {{ title }}
</h1>
```

### Rendering to Terminal

```python
from tempered import Tempered
tempered = Tempered()

html = tempered.render_template(
    "title.html",
    title="hello, world",
)
print(html)
```

```html
>$ python3 quickstart.py
<h1>Hello World</h1>
```

## With Flask

### 1. Install Dependencies

```bash
pip install flask tempered
```

### 2. Setup Flask

```python
from flask import Flask

app = Flask(__name__)

@app.get("/")
def get_index():
    return "<h1>Hello</h1>"

if __name__ == "__main__":
    app.run()
```

### 3. Setup Tempered

```python
from flask import Flask
+ from tempered import Tempered

app = Flask(__name__)
+ tempered = Tempered()

@app.get("/")
def get_index():
    return "<h1>Hello World</h1>"

if __name__ == "__main__":
    app.run()
```

### 4. Add a template

```html
<!-- templates/index.html -->
<h1>
    Hello World
</h1>
```

```python
from flask import Flask
from tempered import Tempered

app = Flask(__name__)
tempered = Tempered()

@app.get("/")
def get_index():
+   return tempered.render_template("index.html")

if __name__ == "__main__":
    app.run()
```

### 5. Using a layout

```html
<!-- templates/layout.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>{% slot required title %}</title>
</head>
<body>
    {% slot %}
</body>
</html>
```

```html
<!-- templates/index.html -->
+ {% layout "layout.html" %}

{% block title %}Home{% endblock %}

<h1>
    Hello World
</h1>
```
