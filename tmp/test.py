import tempered
from folder import types

templates = tempered.Tempered()
templates.add_template(name="test", template="""
    {% param a: A %}
    {{a}}
""")
templates.register_type(types.A)

components = templates.build_static()
print(components.test(a=types.A("test")))
