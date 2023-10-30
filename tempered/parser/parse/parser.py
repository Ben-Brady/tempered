from ...preprocess import generate_scoped_styles, minify_html
from ..parse_ast import *
from ..lexer import *
from .scanner import TokenScanner
from .expr import parse_expr, parse_stmt, parse_ident
from typing import assert_never
import ast


def create_body(scanner: TokenScanner) -> TemplateBlock:
    return take_tags_until(scanner, stop_tags=[])


def take_tags_until(scanner: TokenScanner, stop_tags: list[type[Token]]):
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(scanner)
        if tag:
            tags.append(tag)

    return tags


def next_tag(scanner: TokenScanner) -> TemplateTag|None:
    match scanner.pop():
        case (LiteralToken() | StylesToken() | StylesIncludeToken()) as tag:
            return tag.into_tag()
        case EscapedExprToken(expr_str):
            return ExprBlock(parse_expr(expr_str))
        case HtmlExprToken(expr_str):
            return HtmlBlock(parse_expr(expr_str))
        case ComponentToken(template=template, expr=expr_str):
            return parse_component_block(template, expr_str)
        case SetToken(assignment):
            return parse_set_block(assignment)
        case IfStartToken(condition):
            return next_if(scanner, condition)
        case ForStartToken(variable, iterable):
            return next_for(scanner, variable, iterable)
        case ForEndToken():
            raise ValueError(f"For loop not opened")
        case ElIfToken() | ElseToken() | IfEndToken():
            raise ValueError(f"If statement not openned")
        case ParameterToken():
            return None
        case e:
            assert_never(e)


def parse_component_block(
        template: str,
        expr: str,
        ) -> ComponentBlock:
    call = parse_expr(expr)
    if not isinstance(call, ast.Call):
        raise ValueError("Component call must be a function call")
    keywords = {
        keyword.arg: keyword.value
        for keyword in call.keywords
        if keyword.arg is not None
    }
    return ComponentBlock(
        component_name=template,
        keywords=keywords,
    )


def parse_set_block(assignment: str) -> AssignmentBlock:
    call = parse_stmt(assignment)
    if isinstance(call, ast.Assign):
        if len(call.targets) != 1:
            raise ValueError("Set must have a single target")

        return AssignmentBlock(
            target=call.targets[0],
            value=call.value,
        )
    elif isinstance(call, ast.AnnAssign):
        if call.value is None:
            raise ValueError("Set must have a value")

        return AssignmentBlock(
            target=call.target,
            value=call.value,
        )
    else:
        raise ValueError("Set must be an assignment")



def next_if(
        scanner: TokenScanner,
        condition_str: str,
        ) -> IfBlock:
    condition = parse_expr(condition_str)

    if_block: list[TemplateTag] = take_tags_until(
        scanner=scanner,
        stop_tags=[ElIfToken, ElseToken, IfEndToken]
    )

    elif_blocks: list[tuple[ast.expr, TemplateBlock]] = []
    while scanner.is_next(ElIfToken):
        elif_token = scanner.expect(ElIfToken)
        elif_condition = parse_expr(elif_token.condition)
        block: list[TemplateTag] = take_tags_until(
            scanner,
            stop_tags=[ElIfToken, ElseToken, IfEndToken]
        )
        elif_blocks.append((elif_condition, block))

    else_block: list[TemplateTag] | None = None
    if scanner.accept(ElseToken):
        else_block = take_tags_until(
            scanner=scanner,
            stop_tags=[IfEndToken]
        )

    scanner.expect(IfEndToken)
    return IfBlock(
        condition=condition,
        if_block=if_block,
        else_block=else_block,
        elif_blocks=elif_blocks,
    )


def next_for(
        scanner: TokenScanner,
        variable_str: str,
        iterable_str: str,
        ) -> ForBlock:
    loop_var = parse_ident(variable_str)
    iterable = parse_expr(iterable_str)

    block = take_tags_until(
        scanner=scanner,
        stop_tags=[ForEndToken],
    )
    scanner.expect(ForEndToken)

    return ForBlock(
        loop_block=block,
        iterable=iterable,
        loop_variable=loop_var,
    )
