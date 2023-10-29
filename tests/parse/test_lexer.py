from tempered.parser.lexer import (
    to_token_stream,
    ParameterToken, StylesToken, 
)


def test_parameter_tokens():
    tokens = to_token_stream("""
        {! param a !}
        {! param b !}
    """)
    assert ParameterToken("a") in tokens
    assert ParameterToken("b") in tokens


def test_styles_tokens():
    tokens = to_token_stream("""
        {! styles !}
    """)
    assert StylesToken() in tokens
