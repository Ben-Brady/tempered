from tempered import Tempered


def test_multiple_builds():
    tempered = Tempered()
    tempered.add_template_from_string("foo", "ARRGH")
    a = tempered.build_memory()

    tempered = Tempered()
    tempered.add_template_from_string("foo", "BLARGH")
    tempered.add_template_from_string("bar", "BLARGGHH")
    b = tempered.build_memory()
    print(a, b)
    assert a.foo() == "ARRGH", (a, b)
    assert b.foo() == "BLARGH"
    assert b.bar() == "BLARGGHH"
