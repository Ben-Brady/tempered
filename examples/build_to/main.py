import components
from tempered import Tempered

tempered = Tempered()
tempered.add_template_from_string("Comment", """
    {% param author: str %}
    {% param text: str %}
    <div>
        <h2>{{ author }}</h2>
        <p>{{ text }}</p>
    </div>
""")

tempered.build_to(components)
print(components.Comment(
    author="Ben Brady",
    text="This library is pretty goated"
))

