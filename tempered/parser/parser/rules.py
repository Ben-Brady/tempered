from .. import template_ast, tokens, lexer
from .token_scanner import TokenScanner
from .expr import parse_expr, parse_stmt, parse_ident, parse_parameter
import typing_extensions as t
import ast

if t.TYPE_CHECKING:
    from .parse import ParseContext
else:
    ParseContext = t.Any


T = t.TypeVar("T", bound=tokens.Token)


class Rule(t.Generic[T]):
    token: t.Type[T]

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: T,
    ) -> t.Union[template_ast.Tag, None]:
        ...


class HtmlRule(Rule[tokens.HtmlToken]):
    token = tokens.HtmlToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.HtmlToken,
    ) -> template_ast.HtmlTag:
        return token.into_tag()


class EscapedExprRule(Rule[tokens.EscapedExprToken]):
    token = tokens.EscapedExprToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.EscapedExprToken,
    ) -> template_ast.ExprTag:
        expr = parse_expr(token.expr)
        return template_ast.ExprTag(expr)


class HtmlExprRule(Rule[tokens.HtmlExprToken]):
    token = tokens.HtmlExprToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.HtmlExprToken,
    ) -> template_ast.RawExprTag:
        expr = parse_expr(token.expr)
        return template_ast.RawExprTag(expr)


class StyleIncludedRule(Rule[tokens.StylesIncludeToken]):
    token = tokens.StylesIncludeToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.StylesIncludeToken,
    ) -> None:
        ctx.style_includes.add(token.template)
        return None


class StyleRule(Rule[tokens.StylesToken]):
    token = tokens.StylesToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.StylesToken,
    ) -> template_ast.StyleTag:
        if ctx.styles_set:
            raise ValueError("Template cannot have multiple styles tags")

        ctx.styles_set = True
        return template_ast.StyleTag()


class LayoutRule(Rule[tokens.LayoutToken]):
    token = tokens.LayoutToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.LayoutToken,
    ) -> None:
        if ctx.layout is not None:
            raise ValueError("Template cannot have multiple layout tags")

        layout = ast.literal_eval(token.layout)
        if not isinstance(layout, str):
            raise ValueError("Template names must be a string")

        ctx.layout = layout
        return None


class RuleParameter(Rule[tokens.ParameterToken]):
    token = tokens.ParameterToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.ParameterToken,
    ) -> None:
        param = parse_parameter(token.parameter)
        ctx.parameters.append(param)
        return None


class ComponentRule(Rule[tokens.ComponentToken]):
    token = tokens.ComponentToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.ComponentToken,
    ) -> template_ast.ComponentTag:
        call = parse_expr(token.call)
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
            raise ValueError("Invalid Component Call")

        call = template_ast.ComponentTag(
            component_name=call.func.id,
            keywords={
                keyword.arg: keyword.value
                for keyword in call.keywords
                if keyword.arg is not None
            },
        )
        ctx.components_calls.append(call)
        return call


class SetRule(Rule[tokens.SetToken]):
    token = tokens.SetToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.SetToken,
    ) -> t.Union[template_ast.Tag, None]:
        call = parse_stmt(token.assignment)
        if isinstance(call, ast.Assign):
            if len(call.targets) != 1:
                raise ValueError("Set must have a single target")

            return template_ast.AssignmentTag(
                target=call.targets[0],
                value=call.value,
            )
        elif isinstance(call, ast.AnnAssign):
            if call.value is None:
                raise ValueError("Set must have a value")

            return template_ast.AssignmentTag(
                target=call.target,
                value=call.value,
            )
        else:
            raise ValueError("Set must be an assignment")


class IfRule(Rule[tokens.IfStartToken]):
    token = tokens.IfStartToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.IfStartToken,
    ) -> t.Union[template_ast.Tag, None]:
        condition = parse_expr(token.condition)

        if_block: t.List[template_ast.Tag] = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.ElIfToken, tokens.ElseToken, tokens.IfEndToken],
        )

        elif_blocks: t.List[t.Tuple[ast.expr, template_ast.TemplateBlock]] = []
        while scanner.is_next(tokens.ElIfToken):
            elif_token = scanner.expect(tokens.ElIfToken)
            elif_condition = parse_expr(elif_token.condition)
            block: t.List[template_ast.Tag] = take_tags_until(
                ctx=ctx,
                scanner=scanner,
                stop_tags=[tokens.ElIfToken, tokens.ElseToken, tokens.IfEndToken],
            )
            elif_blocks.append((elif_condition, block))

        else_block: t.Union[t.List[template_ast.Tag], None] = None
        if scanner.accept(tokens.ElseToken):
            else_block = take_tags_until(
                ctx=ctx,
                scanner=scanner,
                stop_tags=[tokens.IfEndToken],
            )

        scanner.expect(tokens.IfEndToken)
        return template_ast.IfTag(
            condition=condition,
            if_block=if_block,
            else_block=else_block,
            elif_blocks=elif_blocks,
        )


class ForRule(Rule[tokens.ForStartToken]):
    token = tokens.ForStartToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.ForStartToken,
    ) -> t.Union[template_ast.Tag, None]:
        loop_var = parse_ident(token.variable)
        iterable = parse_expr(token.iterable)

        block = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.ForEndToken],
        )
        scanner.expect(tokens.ForEndToken)

        return template_ast.ForTag(
            loop_block=block,
            iterable=iterable,
            loop_variable=loop_var,
        )


class SlotRule(Rule[tokens.SlotToken]):
    token = tokens.SlotToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.SlotToken,
    ) -> t.Union[template_ast.Tag, None]:
        ctx.is_layout = True

        if token.name is None:
            if ctx.has_default_slot:
                raise ValueError("Template cannot have multiple default slots")

            ctx.has_default_slot = True
            return template_ast.SlotTag(name=None, default=None)

        if token.is_required:
            default_body = None
        else:
            default_body = take_tags_until(
                ctx=ctx, scanner=scanner, stop_tags=[tokens.SlotEndToken]
            )
            scanner.expect(tokens.SlotEndToken)

        slot = template_ast.SlotTag(
            name=token.name,
            default=default_body,
        )
        ctx.slots.append(slot)
        return slot


class BlockRule(Rule[tokens.BlockStartToken]):
    token = tokens.BlockStartToken

    @staticmethod
    def take(
        ctx: ParseContext,
        scanner: TokenScanner,
        token: tokens.BlockStartToken,
    ) -> t.Union[template_ast.Tag, None]:
        ctx.blocks.add(token.name)
        body = take_tags_until(
            ctx=ctx,
            scanner=scanner,
            stop_tags=[tokens.BlockEndToken],
        )
        scanner.expect(tokens.BlockEndToken)

        return template_ast.BlockTag(
            name=token.name,
            body=body,
        )


rules: t.List[Rule] = [
    SlotRule(),
    StyleRule(),
    LayoutRule(),
    RuleParameter(),
    ComponentRule(),
    SetRule(),
    IfRule(),
    ForRule(),
    BlockRule(),
    HtmlRule(),
    EscapedExprRule(),
    HtmlExprRule(),
    StyleIncludedRule(),
]


def next_tag(
    ctx: ParseContext, scanner: TokenScanner
) -> t.Union[template_ast.Tag, None]:
    tag = scanner.pop()
    for rule in rules:
        if isinstance(tag, rule.token):
            return rule.take(ctx, scanner, tag)

    if isinstance(tag, tokens.SlotEndToken):
        raise ValueError("Slot not opened")
    elif isinstance(tag, tokens.BlockEndToken):
        raise ValueError("Block not opened")
    elif isinstance(tag, (tokens.ElIfToken, tokens.ElseToken, tokens.IfEndToken)):
        raise ValueError("If statement not openned")
    elif isinstance(tag, tokens.ForEndToken):
        raise ValueError("For loop not opened")
    else:
        raise ValueError("Unknown Tag")


def take_tags_until(
    ctx: ParseContext,
    scanner: TokenScanner,
    stop_tags: t.List[t.Type[tokens.Token]] = [],
) -> t.List[template_ast.Tag]:
    tags = []
    while scanner.has_tokens:
        if scanner.is_next(*stop_tags):
            break

        tag = next_tag(ctx, scanner)
        if tag:
            tags.append(tag)

    return tags
