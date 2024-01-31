from __future__ import annotations
import ast
import typing_extensions as t
from .. import ast_utils
from ..parser.template_ast import (
    AssignmentNode,
    BlockNode,
    ComponentNode,
    ExprNode,
    ForNode,
    HtmlNode,
    IfNode,
    ImportNode,
    Node,
    RawExprNode,
    SlotNode,
    StyleNode,
)
from .calls import create_escape_call, slot_parameter, slot_variable_name
from .constants import CSS_VARIABLE, KWARGS_VAR, NAME_LOOKUP_VAR, WITH_STYLES

if t.TYPE_CHECKING:
    from .builder import BuildContext
else:
    BuildContext = t.Any

RuleReturnType: t.TypeAlias = t.Union[t.Iterable[ast.stmt], None]


def construct_html(ctx: BuildContext, tag: HtmlNode) -> RuleReturnType:
    yield ctx.add_expr(ast_utils.Constant(tag.html))


def construct_expr(ctx: BuildContext, tag: ExprNode) -> RuleReturnType:
    yield ctx.add_expr(create_escape_call(value=tag.value))


def construct_raw_expr(ctx: BuildContext, tag: RawExprNode) -> RuleReturnType:
    yield ctx.add_expr(tag.value)


def construct_assign(ctx: BuildContext, tag: AssignmentNode) -> RuleReturnType:
    yield ast_utils.Assign(
        target=tag.target,
        value=tag.value,
    )


def construct_import(ctx: BuildContext, tag: ImportNode) -> RuleReturnType:
    template_func = ast_utils.Index(
        ast_utils.Name(NAME_LOOKUP_VAR),
        ast_utils.Constant(tag.name),
    )
    yield ast_utils.Assign(
        target=tag.target,
        value=template_func,
    )


def construct_if(ctx: BuildContext, tag: IfNode) -> RuleReturnType:
    ctx.ensure_output_assigned()
    EMPTY_BODY = [ast_utils.create_stmt("...", ast.Expr)]

    # {% if %}
    if_body = ctx.create_block(tag.if_block) or EMPTY_BODY

    # {% elif %}
    elif_blocks: t.List[t.Tuple[ast.expr, t.Sequence[ast.stmt]]] = []
    for condition, elif_block in tag.elif_blocks:
        elif_body = ctx.create_block(elif_block)
        if len(elif_body) != 0:
            elif_blocks.append((condition, elif_body))

    # {% else %}
    if tag.else_block:
        else_body = ctx.create_block(tag.else_block) or EMPTY_BODY
    else:
        else_body = None

    yield ast_utils.If(
        condition=tag.condition,
        if_body=if_body,
        elif_blocks=elif_blocks,
        else_body=else_body,
    )


def construct_for(ctx: BuildContext, tag: ForNode) -> RuleReturnType:
    ctx.ensure_output_assigned()

    for_body = ctx.create_block(tag.loop_block)
    if len(for_body) > 0:
        yield ast.For(
            target=tag.target,
            iter=tag.iterable,
            body=for_body,
            orelse=[],
        )


def construct_block(ctx: BuildContext, tag: BlockNode) -> RuleReturnType:
    yield from ctx.save_block_output_to_variable(
        output=slot_variable_name(tag.name),
        tags=tag.body,
    )


def construct_slot(ctx: BuildContext, tag: SlotNode) -> RuleReturnType:
    slot_param = ast_utils.Name(slot_parameter(tag.name))

    if tag.default is None:
        yield ctx.add_expr(slot_param)
        return

    if_stmt = ast_utils.If(
        condition=ast_utils.Is(slot_param, ast_utils.None_),
        if_body=ctx.save_block_output_to_variable(
            output=slot_param,
            tags=tag.default,
        ),
    )
    yield if_stmt
    yield ctx.add_expr(slot_param)


def construct_styles(ctx: BuildContext, tag: StyleNode) -> RuleReturnType:
    if ctx.uses_layout:
        return  # Styles are placed in the layout template
    if ctx.css is None and not ctx.is_layout:
        return

    ctx.ensure_output_assigned()
    if not ctx.is_layout:
        condition = ast_utils.Name(WITH_STYLES)
        value = ast_utils.Constant(f"<style>{ctx.css}</style>")
    else:
        condition = ast_utils.And(
            ast_utils.Name(WITH_STYLES),
            ast_utils.Name(CSS_VARIABLE),
        )
        value = ast_utils.FormatString(
            ast_utils.Constant("<style>"),
            ast_utils.Name(CSS_VARIABLE),
            ast_utils.Constant("</style>"),
        )

    yield ast_utils.If(
        condition=condition,
        if_body=ctx.output_variable.create_add(value),
    )


def construct_component(ctx: BuildContext, tag: ComponentNode) -> RuleReturnType:
    func = ast_utils.Name(tag.component_name)
    keywords = tag.keywords.copy()

    keywords[WITH_STYLES] = ast_utils.Constant(False)
    func_call = ast_utils.Call(
        func=func,
        keywords=keywords,
        kwargs=ast_utils.Name(KWARGS_VAR),
    )
    yield ctx.add_expr(func_call)


T = t.TypeVar("T", bound=Node, infer_variance=True)
Rule: t.TypeAlias = t.Tuple[
    t.Type[T],
    t.Callable[[BuildContext, T], RuleReturnType],
]

default_rules: t.List[Rule] = [
    (HtmlNode, construct_html),
    (ExprNode, construct_expr),
    (ComponentNode, construct_component),
    (RawExprNode, construct_raw_expr),
    (AssignmentNode, construct_assign),
    (ImportNode, construct_import),
    (IfNode, construct_if),
    (ForNode, construct_for),
    (SlotNode, construct_slot),
    (BlockNode, construct_block),
    (StyleNode, construct_styles),
]
