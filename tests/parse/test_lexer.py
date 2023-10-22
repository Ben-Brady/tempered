from tempered.parser.lexer import to_token_stream, ParameterToken


def test_parameter_tokens():
    tokens = to_token_stream("""
        {! param a !}
        {! param b !}
    """)
    assert ParameterToken("a") in tokens
    assert ParameterToken("b") in tokens

