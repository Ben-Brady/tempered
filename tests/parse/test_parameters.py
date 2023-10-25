from tempered.parser import parse_template, TemplateParameter, RequiredParameter, LiteralBlock
import ast


def _assert_parameter_required(parameter: TemplateParameter):
    assert isinstance(parameter.default, RequiredParameter)


def test_parse_removes_parameters():
    template = parse_template("abc", """
        {!param a!}
        {!param b!}
    """)
    block = template.body[0]
    assert isinstance(block, LiteralBlock)
    assert block.body == "" or block.body.isspace()


def test_parse_parameter():
    template = parse_template("abc", """
        {!param a !}
    """)
    assert TemplateParameter(name="a") in template.parameters
    _assert_parameter_required(template.parameters[0])


def test_parse_parameters_with_builtin_annotation():
    template = parse_template("abc", """
        {!param a: str !}
    """)
    assert template.parameters[0].name == "a"
    assert ast.unparse(template.parameters[0].type) == "str"
    _assert_parameter_required(template.parameters[0])


def test_parse_parameters_with_custom_annotation():
    template = parse_template("abc", """
        {!param a: Post !}
    """)

    _assert_parameter_required(template.parameters[0])
    assert template.parameters[0].name == "a"
    assert ast.unparse(template.parameters[0].type) == "Post"


def test_parse_parameters_with_default():
    template = parse_template("abc", """
        {!param a = 1!}
    """)
    assert TemplateParameter(name="a", default=1) in template.parameters


def test_parse_parameters_with_annotation_and_default():
    template = parse_template("abc", """
        {!param a: int = 1!}
    """)

    assert template.parameters[0].name == "a"
    assert ast.unparse(template.parameters[0].type) == "int"
    assert template.parameters[0].default == 1


def test_parse_parameters_with_complex_annotation():
    template = parse_template("abc", """
        {!param a: list[str]!}
    """)

    assert template.parameters[0].name == "a"
    assert ast.unparse(template.parameters[0].type) == "list[str]"
