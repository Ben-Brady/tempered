from tempered import Tempered

tempered = Tempered(
    generate_types=False,
)

tempered.add_from_string("heading", """
{% param title: str %}

<h1>{{ title }}</h1>
""")

print(tempered.render("heading", title="foo"))
