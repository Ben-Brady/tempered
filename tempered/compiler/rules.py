from __future__ import annotations
import ast
import typing_extensions as t
from .. import ast_utils
from ..parser import template_ast as tags
from .constants import (
    CSS_VARIABLE,
    KWARGS_VARIABLE,
    WITH_STYLES_PARAMETER,
    create_escape_call,
    slot_parameter,
    slot_variable_name,
)

if t.TYPE_CHECKING:
    from .builder import BuildContext


T = t.TypeVar("T", bound=tags.Node, infer_variance=True)


class Rule(t.Generic[T]):
    tag: t.Type[T]

    @staticmethod
    def construct(ctx: BuildContext, tag: T):
        raise NotImplementedError


class HtmlRule(Rule[tags.HtmlNode]):
    tag = tags.HtmlNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.HtmlNode):
        ctx.add_expr(ast_utils.Constant(tag.html))


class ExprRule(Rule[tags.ExprNode]):
    tag = tags.ExprNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ExprNode):
        ctx.add_expr(create_escape_call(value=tag.value))


class RawExprRule(Rule[tags.RawExprNode]):
    tag = tags.RawExprNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.RawExprNode):
        ctx.add_expr(tag.value)


class AssignmentRule(Rule[tags.AssignmentNode]):
    tag = tags.AssignmentNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.AssignmentNode):
        assign = ast_utils.Assign(
            target=tag.target,
            value=tag.value,
        )
        ctx.body.append(assign)


class ImportRule(Rule[tags.ImportNode]):
    tag = tags.ImportNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ImportNode):
        template_func = ast_utils.Index(
            ast_utils.Name("_name_lookup"),
            ast_utils.Constant(tag.name),
        )
        assign = ast_utils.Assign(
            target=tag.target,
            value=template_func,
        )
        ctx.body.append(assign)


class IfRule(Rule[tags.IfNode]):
    tag = tags.IfNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.IfNode):
        ctx.ensure_output_assigned()

        empty_body = [ast_utils.create_stmt("...", ast.Expr)]
        if_body = ctx.create_block(tag.if_block) or empty_body

        elif_blocks: t.List[t.Tuple[ast.expr, t.Sequence[ast.stmt]]] = []
        for condition, elif_block in tag.elif_blocks:
            elif_body = ctx.create_block(elif_block) or empty_body
            elif_blocks.append((condition, elif_body))

        if tag.else_block:
            else_body = ctx.create_block(tag.else_block) or empty_body
        else:
            else_body = None

        ctx.body.append(
            ast_utils.If(
                condition=tag.condition,
                if_body=if_body,
                elif_blocks=elif_blocks,
                else_body=else_body,
            )
        )


class ForRule(Rule[tags.ForNode]):
    tag = tags.ForNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ForNode):
        ctx.ensure_output_assigned()

        for_body = ctx.create_block(tag.loop_block)
        if len(for_body) > 0:
            ctx.body.append(
                ast.For(
                    target=tag.loop_variable,
                    iter=tag.iterable,
                    body=for_body,
                    orelse=[],
                )
            )


class BlockRule(Rule[tags.BlockNode]):
    tag = tags.BlockNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.BlockNode):
        ctx.body.extend(
            ctx.create_variable(
                name=slot_variable_name(tag.name),
                tags=tag.body,
            )
        )


class SlotRule(Rule[tags.SlotNode]):
    tag = tags.SlotNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.SlotNode):
        slot_param = ast_utils.Name(slot_parameter(tag.name))

        if tag.default is None:
            ctx.add_expr(slot_param)
            return

        if_stmt = ast_utils.If(
            condition=ast_utils.Is(slot_param, ast_utils.None_),
            if_body=ctx.create_variable(
                name=slot_param,
                tags=tag.default,
            ),
        )
        ctx.body.append(if_stmt)
        ctx.add_expr(slot_param)


class StyleRule(Rule[tags.StyleNode]):
    tag = tags.StyleNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.StyleNode):
        if ctx.uses_layout:
            return  # Styles are placed in the layout template
        if ctx.css is None and not ctx.is_layout:
            return

        ctx.ensure_output_assigned()
        if not ctx.is_layout:
            condition = ast_utils.Name(WITH_STYLES_PARAMETER)
            value = ast_utils.Constant(f"<style>{ctx.css}</style>")
        else:
            condition = ast_utils.And(
                ast_utils.Name(WITH_STYLES_PARAMETER),
                ast_utils.Name(CSS_VARIABLE),
            )
            value = ast_utils.FormatString(
                ast_utils.Constant("<style>"),
                ast_utils.Name(CSS_VARIABLE),
                ast_utils.Constant("</style>"),
            )

        ctx.body.append(
            ast_utils.If(
                condition=condition,
                if_body=ctx.output_variable.create_add(value),
            )
        )


class ComponentRule(Rule[tags.ComponentNode]):
    tag = tags.ComponentNode

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ComponentNode):
        func = ast_utils.Name(tag.component_name)
        keywords = tag.keywords.copy()

        keywords[WITH_STYLES_PARAMETER] = ast_utils.Constant(False)
        func_call = ast_utils.Call(
            func=func,
            keywords=keywords,
            kwargs=ast_utils.Name(KWARGS_VARIABLE),
        )
        ctx.add_expr(func_call)


default_rules: t.List[type[Rule]] = [
    HtmlRule,
    ExprRule,
    RawExprRule,
    ComponentRule,
    AssignmentRule,
    IfRule,
    ForRule,
    StyleRule,
    BlockRule,
    SlotRule,
    ImportRule,
]
