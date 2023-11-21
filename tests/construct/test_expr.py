from . import build_template
from tempered.parser import Template, parse_ast
import ast
import bs4

def test_expr_block():
    literal = "example text"
    func = build_template(Template(
        name="expr",
        body=[parse_ast.ExprBlock(ast.Constant(value=literal))],
    ))
    assert func() == "example text", "Expression isn't placed"


def test_expr_block_escapes_tags():
    literal = "<script>"
    func = build_template(Template(
        name="expr",
        body=[parse_ast.ExprBlock(ast.Constant(value=literal))],
    ))
    assert func() != literal, "Expression isn't escaped"


def test_expr_block_param():
    link = "/test"
    func = build_template(Template(
        name="expr",
        body=[
            parse_ast.LiteralBlock("<a href='"),
            parse_ast.ExprBlock(ast.Constant(value=link)),
            parse_ast.LiteralBlock("'></a>"),
        ],
    ))
    assert func() == "<a href='/test'></a>", "Expression isn't escaped"


def test_expr_block_escapes_param():
    link = "/test' onerror='alert(1)"
    func = build_template(Template(
        name="expr",
        body=[
            parse_ast.LiteralBlock("<a href='"),
            parse_ast.ExprBlock(ast.Constant(value=link)),
            parse_ast.LiteralBlock("'></a>"),
        ],
    ))
    HTML = func()
    a_tag = bs4.BeautifulSoup(HTML, "html.parser").find("a")
    assert isinstance(a_tag, bs4.Tag), "Expression isn't escaped"
    assert "onerror" not in a_tag.attrs, "Expression isn't escaped"
    assert list(a_tag.attrs.keys()) == ["href"], "Expression isn't escaped"


def test_multiple_expr_chained():
    func = build_template(Template(
        name="expr",
        body=[
            parse_ast.LiteralBlock("1"),
            parse_ast.ExprBlock(ast.Constant(value="a")),
            parse_ast.LiteralBlock("2"),
            parse_ast.ExprBlock(ast.Constant(value="b")),
            parse_ast.LiteralBlock("3"),
            parse_ast.ExprBlock(ast.Constant(value="c")),
        ],
    ))
    assert func() == "1a2b3c"
