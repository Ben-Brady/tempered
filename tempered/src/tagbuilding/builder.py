from __future__ import annotations
import ast
import typing_extensions as t
from .tags import (
    Tag, IfStartTag, ElIfTag, ElseTag, IfEndTag,
    ForStartTag, ForEndTag, SlotStartTag, SlotEndTag,
    BlockStartTag, BlockEndTag, LayoutTag, IncludeTag, ParameterTag
)
from ..lexing import lexer
from ..utils import ast_utils
from ..parsing import nodes
from ..utils.scanner import Scanner


TokenScanner: t.TypeAlias = Scanner[lexer.Token]


def parse_tokens_to_tags(stream: t.Sequence[lexer.Token]) -> t.Sequence[Tag]:
    scanner = Scanner(stream)
    return list(_take_body(scanner))


def _take_body(scanner: TokenScanner) -> t.Iterable[Tag]:
    while scanner.has_tokens:
        yield _next_tag(scanner)


def _next_tag(scanner: TokenScanner) -> Tag:
    if scanner.is_next(lexer.StatementStartToken):
        return next_statement_tag(scanner)
    elif scanner.is_next(lexer.ExprStartToken):
        return _next_expr_tag(scanner)

    token = scanner.pop()
    if isinstance(token, lexer.HtmlToken):
        return nodes.HtmlNode(token.html)
    else:
        raise ValueError(f"Unknown token {token}")


def _next_expr_tag(scanner: TokenScanner) -> Tag:
    scanner.expect(lexer.ExprStartToken)
    expr = take_python_expr(scanner)
    scanner.expect(lexer.ExprEndToken)
    return nodes.ExprNode(expr)


def next_statement_tag(scanner: TokenScanner) -> Tag:
    scanner.expect(lexer.StatementStartToken)
    keyword = scanner.expect(lexer.KeywordToken).keyword

    statement_funcs: t.Dict[str, t.Callable[[TokenScanner], Tag]] = {
        "if": lambda _: IfStartTag(take_python_expr(scanner)),
        "elif": lambda _: ElIfTag(take_python_expr(scanner)),
        "else": lambda _: ElseTag(),
        "endif": lambda _: IfEndTag(),
        "for": _next_for_token,
        "endfor": lambda _: ForEndTag(),
        "slot": _next_slot_tag,
        "endslot": lambda _: SlotEndTag(),
        "block": lambda _: BlockStartTag(take_ident_token(scanner)),
        "endblock": lambda _: BlockEndTag(),
        "html": lambda _: nodes.RawExprNode(take_python_expr(scanner)),
        "set": _next_assign_tag,
        "layout": lambda _: LayoutTag(take_string_token(scanner)),
        "styles": lambda _: nodes.StyleNode(),
        "include": lambda _: IncludeTag(take_string_token(scanner)),
        "import": _next_import_tag,
        "param": _next_param_tag,
        "component": _next_component_tag,
    }
    tag = statement_funcs[keyword](scanner)
    scanner.expect(lexer.StatementEndToken)
    return tag


def _next_component_tag(scanner: TokenScanner) -> Tag:
    call = take_python_expr(scanner, ast.Call)
    if not isinstance(call.func, ast.Name):
        raise ValueError("Component call must be a name")

    keywords = {
        keyword.arg: keyword.value
        for keyword in call.keywords
        if keyword.arg is not None
    }
    return nodes.ComponentNode(
        component_name=call.func.id,
        keywords=keywords,
    )


def _next_assign_tag(scanner: TokenScanner) -> Tag:
    target = scanner.expect(lexer.IdentToken).name
    expect_keyword(scanner, "=")
    expr = take_python_expr(scanner)
    return nodes.AssignmentNode(
        target=ast_utils.Name(target),
        value=expr,
    )


def _next_import_tag(scanner: TokenScanner) -> Tag:
    target = scanner.expect(lexer.IdentToken).name
    expect_keyword(scanner, "from")
    name = take_string_token(scanner)
    return nodes.ImportNode(
        target=target,
        name=name,
    )


def _next_param_tag(scanner: TokenScanner) -> Tag:
    expr = take_python_stmt(scanner)

    if isinstance(expr, ast.AnnAssign) and isinstance(expr.target, ast.Name):
        # name: type | name: type = default
        return ParameterTag(
            name=expr.target.id,
            type=expr.annotation,
            default=expr.value,
        )
    elif (
        isinstance(expr, ast.Assign)
        and isinstance(expr.targets, list)
        and isinstance(expr.targets[0], ast.Name)
    ):
        # name = default
        return ParameterTag(
            name=expr.targets[0].id,
            default=expr.value,
        )
    elif isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Name):
        # name
        return ParameterTag(name=expr.value.id)
    else:
        raise ValueError(f"Invalid Parameter: {expr}")


def _next_slot_tag(scanner: TokenScanner) -> Tag:
    if scanner.is_next(lexer.IdentToken):
        name = take_ident_token(scanner)
    else:
        name = None

    if scanner.is_next(lexer.KeywordToken):
        expect_keyword(scanner, "required")
        is_required = True
    else:
        is_required = False

    return SlotStartTag(name, is_required)


def _next_for_token(scanner: TokenScanner) -> Tag:
    ident = scanner.expect(lexer.IdentToken).name

    loop_variables = [ident]
    while accept_keyword(scanner, ","):
        loop_variables.append(take_ident_token(scanner))

    expect_keyword(scanner, "in")
    iterable = take_python_expr(scanner)
    if len(loop_variables) != 1:
        target = ast_utils.Tuple(ast_utils.Name(name) for name in loop_variables)
    else:
        target = ast_utils.Name(loop_variables[0])

    return ForStartTag(iterable, target)


def take_string_token(scanner: TokenScanner) -> str:
    string_token = scanner.expect(lexer.StringToken)
    return string_token.string


def take_ident_token(scanner: TokenScanner) -> str:
    ident_token = scanner.expect(lexer.IdentToken)
    return ident_token.name


TExpr = t.TypeVar("TExpr", bound=ast.expr)
TStmt = t.TypeVar("TStmt", bound=ast.stmt)


def take_python_expr(scanner: TokenScanner, type: t.Type[TExpr] = ast.expr) -> TExpr:
    token = scanner.expect(lexer.PythonExprToken)
    return ast_utils.create_expr(token.expr, type)


def take_python_stmt(scanner: TokenScanner, type: t.Type[TStmt] = ast.stmt) -> TStmt:
    token = scanner.expect(lexer.PythonStmtToken)
    return ast_utils.create_stmt(token.stmt, type)


def accept_keyword(scanner: TokenScanner, keyword: str) -> bool:
    if not scanner.is_next(lexer.KeywordToken):
        return False

    keyword_token = t.cast(lexer.KeywordToken, scanner.peek())
    if keyword_token.keyword == keyword:
        scanner.pop()
        return True
    else:
        return False


def expect_keyword(scanner: TokenScanner, keyword: str):
    keyword_token = scanner.expect(lexer.KeywordToken)
    if keyword_token.keyword != keyword:
        raise ValueError(f"Expected keyword {keyword}")
