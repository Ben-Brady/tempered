from . import build_template
from tempered.parser import Template, LiteralBlock, ExprBlock
import ast
import bs4

def test_expr_block():
    literal = "example text"
    func = build_template(Template(
        name="expr",
        body=[ExprBlock(ast.Constant(value=literal))],
    ))
    assert func() == "example text", "Expression isn't placed"


def test_expr_block_escapes_tags():
    literal = "<script>"
    func = build_template(Template(
        name="expr",
        body=[ExprBlock(ast.Constant(value=literal))],
    ))
    assert func() != literal, "Expression isn't escaped"


def test_expr_block_param():
    link = "/test"
    func = build_template(Template(
        name="expr",
        body=[
            LiteralBlock("<a href='"),
            ExprBlock(ast.Constant(value=link)),
            LiteralBlock("'></a>"),
        ],
    ))
    assert func() == "<a href='/test'></a>", "Expression isn't escaped"


def test_expr_block_escapes_param():
    link = "/test' onerror='alert(1)"
    func = build_template(Template(
        name="expr",
        body=[
            LiteralBlock("<a href='"),
            ExprBlock(ast.Constant(value=link)),
            LiteralBlock("'></a>"),
        ],
    ))
    HTML = func()
    a_tag = bs4.BeautifulSoup(HTML, "html.parser").find("a")
    assert isinstance(a_tag, bs4.Tag), "Expression isn't escaped"
    assert "onerror" not in a_tag.attrs, "Expression isn't escaped"
    assert list(a_tag.attrs.keys()) == ["href"], "Expression isn't escaped"
