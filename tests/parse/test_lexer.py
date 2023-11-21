from tempered.parser.lexer import to_token_stream
from tempered.parser import tokens


def test_parameter_tokens():
    tokens_ = to_token_stream("""
        {% param a %}
        {% param b %}
    """)
    assert tokens.ParameterToken("a") in tokens_
    assert tokens.ParameterToken("b") in tokens_


def test_styles_tokens():
    tokens_ = to_token_stream("""
        {% styles %}
    """)
    assert tokens.StylesToken() in tokens_
