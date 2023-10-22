from tempered.parser import parse_template, TemplateParameter, RequiredParameter, LiteralBlock


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
    assert TemplateParameter(name="a", type="str") in template.parameters
    _assert_parameter_required(template.parameters[0])


def test_parse_parameters_with_custom_annotation():
    template = parse_template("abc", """
        {!param a: Post !}
    """)
    assert TemplateParameter(name="a", type="Post") in template.parameters
    _assert_parameter_required(template.parameters[0])


def test_parse_parameters_with_default():
    template = parse_template("abc", """
        {!param a = 1!}
    """)
    assert TemplateParameter(name="a", default=1) in template.parameters


def test_parse_parameters_with_annotation_and_default():
    template = parse_template("abc", """
        {!param a: int = 1!}
    """)
    assert TemplateParameter(name="a", type="int", default=1) in template.parameters

def test_parse_parameters_with_complex_annotation():
    template = parse_template("abc", """
        {!param a: list[str]!}
    """)
    assert TemplateParameter(name="a", type="list[str]") in template.parameters
