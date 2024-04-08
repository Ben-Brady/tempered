# Basic Setup

## 1. Installing tempered

```bash
pip install tempered
```

## 2. Create your First Template

```html
<!-- templates/title.html -->
<h1>
    {{ title }}
</h1>
```

### 3. Rendering to Terminal

```python
from tempered import Tempered

tempered = Tempered(
    template_folder="./templates",
)

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
