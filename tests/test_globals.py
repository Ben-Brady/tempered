from tempered import Tempered

def test_globals_are_accessble_in_templates():
    tempered = Tempered()
    tempered.add_template_from_string("test", """
        {format_str()}
    """)
    components = tempered.build_memory()
