from tempered import ast_utils
from tempered.parser import parse_template, template_ast
import ast
import typing_extensions as t
import pytest


class Unset:
    pass


def _assert_single_parameter(
    template_str,
    *,
    name: str,
    type: t.Union[str, None] = None,
    default: t.Union[t.Any, Unset] = Unset(),
):
    template = parse_template("_", template_str)
    parameters = template.parameters

    assert len(parameters) == 1
    param = parameters[0]
    assert param.name == name
    if type:
        assert param.type
        assert ast_utils.unparse(param.type) == type

    if isinstance(default, Unset):
        assert param.default == None
    else:
        assert param.default is not None
        assert ast.literal_eval(param.default) == default


def test_parse_removes_parameters():
    template = parse_template("abc", "{%param a%}" "{%param b%}" "a")
    block = template.body[0]
    assert isinstance(block, template_ast.LiteralTag)
    assert "a" in block.body


def test_parse_parameter_single():
    _assert_single_parameter("{%param a %}", name="a")


def test_parse_parameters_with_builtin_annotation():
    _assert_single_parameter(
        "{%param a: str %}",
        name="a",
        type="str",
    )


def test_parse_parameters_with_custom_annotation():
    _assert_single_parameter("{%param a: Post %}", name="a", type="Post")


def test_parse_parameters_with_default():
    _assert_single_parameter(
        "{%param a = 1%}",
        name="a",
        default=1,
    )


def test_parse_parameters_with_none_default():
    _assert_single_parameter(
        "{%param a: str|None = None %}",
        name="a",
        type="str | None",
        default=None,
    )


def test_parse_parameters_with_annotation_and_default():
    _assert_single_parameter(
        "{%param a: int = 1%}",
        name="a",
        type="int",
        default=1,
    )


def test_parse_parameters_with_complex_annotation():
    _assert_single_parameter(
        "{%param a: t.List[str]%}",
        name="a",
        type="t.List[str]",
    )


@pytest.mark.skip
def test_parse_parameters_with_end_statement_default():
    _assert_single_parameter(
        "{%param a = '%}' %}",
        name="a",
        default="%}",
    )


@pytest.mark.skip
def test_parse_parameters_with_multiline_string_default():
    _assert_single_parameter(
        """{%param a =
        '''
        a
        '''
        """,
        name="a",
        default="%}",
    )
