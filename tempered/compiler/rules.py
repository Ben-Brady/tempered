from __future__ import annotations
import typing_extensions as t
from .. import ast_utils
from ..parser import template_ast as tags
from .utils import (
    create_escape_call,
    slot_variable_name,
    slot_parameter,
    WITH_STYLES_PARAMETER,
    CSS_VARIABLE,
    KWARGS_VARIABLE,
)
import ast
import typing_extensions as t

if t.TYPE_CHECKING:
    from .builder import BuildContext


T = t.TypeVar("T", bound=tags.Tag, infer_variance=True)


class Rule(t.Generic[T]):
    tag: t.Type[T]

    @staticmethod
    def construct(ctx: BuildContext, tag: T):
        raise NotImplementedError


class LiteralRule(Rule[tags.LiteralTag]):
    tag = tags.LiteralTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.LiteralTag):
        ctx.add_expr(ast_utils.Constant(tag.body))


class ExprRule(Rule[tags.ExprTag]):
    tag = tags.ExprTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ExprTag):
        ctx.add_expr(create_escape_call(value=tag.value))


class RawExprRule(Rule[tags.RawExprTag]):
    tag = tags.RawExprTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.RawExprTag):
        ctx.add_expr(tag.value)


class AssignmentRule(Rule[tags.AssignmentTag]):
    tag = tags.AssignmentTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.AssignmentTag):
        ctx.body.append(
            ast_utils.Assign(
                target=tag.target,
                value=tag.value,
            )
        )


class IfRule(Rule[tags.IfTag]):
    tag = tags.IfTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.IfTag):
        ctx.ensure_output_assigned()

        if_body = ctx.create_block(tag.if_block)

        elif_blocks: t.List[t.Tuple[ast.expr, t.Sequence[ast.stmt]]] = []
        for condition, elif_block in tag.elif_blocks:
            elif_body = ctx.create_block(elif_block)
            elif_blocks.append((condition, elif_body))

        if tag.else_block:
            else_body = ctx.create_block(tag.else_block)
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


class ForRule(Rule[tags.ForTag]):
    tag = tags.ForTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ForTag):
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


class BlockRule(Rule[tags.BlockTag]):
    tag = tags.BlockTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.BlockTag):
        ctx.body.extend(
            ctx.create_variable(
                name=slot_variable_name(tag.name),
                tags=tag.body,
            )
        )


class SlotRule(Rule[tags.SlotTag]):
    tag = tags.SlotTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.SlotTag):
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


class StyleRule(Rule[tags.StyleTag]):
    tag = tags.StyleTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.StyleTag):
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


class ComponentRule(Rule[tags.ComponentTag]):
    tag = tags.ComponentTag

    @staticmethod
    def construct(ctx: BuildContext, tag: tags.ComponentTag):
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
    LiteralRule,
    ExprRule,
    RawExprRule,
    ComponentRule,
    AssignmentRule,
    IfRule,
    ForRule,
    StyleRule,
    BlockRule,
    SlotRule,
]
