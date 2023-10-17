from tempered import _internals as internals


def test_escape_str():
    assert "foo" == internals.escape("foo")
    assert "<script>" != internals.escape("<script>")
