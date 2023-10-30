from tempered.parser import parse_template, TemplateParameter, RequiredParameter, LiteralBlock
import ast
from typing import Any
import pytest


def _assert_single_parameter(
    template_str, *,
    name: str,
    type: str|None = None,
    default: Any|RequiredParameter = RequiredParameter()
):
    template = parse_template("_", template_str)
    parameters = template.parameters

    assert len(parameters) == 1
    param = parameters[0]
    assert param.name == name
    if type:
        assert param.type
        assert ast.unparse(param.type) == type

    if isinstance(default, RequiredParameter):
        assert isinstance(param.default, RequiredParameter)
    else:
        assert not isinstance(param.default, RequiredParameter)
        assert ast.literal_eval(param.default) == default


def test_parse_removes_parameters():
    template = parse_template("abc", """
        {!param a!}
        {!param b!}
    """)
    block = template.body[0]
    assert isinstance(block, LiteralBlock)
    assert block.body == "" or block.body.isspace()


def test_parse_parameter_single():
    _assert_single_parameter(
        "{!param a !}",
        name="a"
    )


def test_parse_parameters_with_builtin_annotation():
    _assert_single_parameter(
        "{!param a: str !}",
        name="a",
        type="str",
    )


def test_parse_parameters_with_custom_annotation():
    _assert_single_parameter(
        "{!param a: Post !}",
        name="a",
        type="Post"
    )


def test_parse_parameters_with_default():
    _assert_single_parameter(
        "{!param a = 1!}",
        name="a",
        default=1,
    )


def test_parse_parameters_with_none_default():
    _assert_single_parameter(
        "{!param a: str|None = None !}",
        name="a",
        type="str | None",
        default=None,
    )

def test_parse_parameters_with_annotation_and_default():
    _assert_single_parameter(
        "{!param a: int = 1!}",
        name="a",
        type="int",
        default=1,
    )


def test_parse_parameters_with_complex_annotation():
    _assert_single_parameter(
        "{!param a: list[str]!}",
        name="a",
        type="list[str]",
    )


@pytest.mark.skip
def test_parse_parameters_with_end_statement_default():
    _assert_single_parameter(
        "{!param a = '!}' !}",
        name="a",
        default="!}",
    )


@pytest.mark.skip
def test_parse_parameters_with_multiline_string_default():
    _assert_single_parameter(
        """{!param a =
        '''
        a
        '''
        """,
        name="a",
        default="!}",
    )
