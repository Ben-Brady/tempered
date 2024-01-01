from __future__ import annotations
from ..parser.template_ast import (
    Template,
    LayoutTemplate,
    Tag,
)
from .accumulators import Variable
import ast
from dataclasses import dataclass, field
import typing_extensions as t

if t.TYPE_CHECKING:
    from .rules import Rule


@dataclass
class BuildContext:
    template: Template
    layout: t.Optional[LayoutTemplate]
    css: t.Optional[str]
    output_variable: Variable
    rules: list[t.Type[Rule]]
    css_variable: t.Optional[Variable] = None
    body: t.List[ast.stmt] = field(default_factory=list)

    @property
    def uses_layout(self):
        return self.layout is not None

    @property
    def is_layout(self):
        return self.template.is_layout

    def add_expr(self, expr: ast.expr):
        self.body.append(self.output_variable.create_add(expr))

    def ensure_output_assigned(self):
        if not self.output_variable.assigned:
            self.body.extend(self.output_variable.assign())

    def construct_tag(self, tag: Tag):
        rules = {rule.tag: rule for rule in self.rules}
        rule = rules.get(type(tag))
        if rule is None:
            raise NotImplementedError(f"Tag {tag} not implemented")

        rule.construct(self, tag)

    def create_block(self, tags: t.Sequence[Tag]) -> t.Sequence[ast.stmt]:
        ctx_block = self.create_subcontext()
        for tag in tags:
            ctx_block.construct_tag(tag)

        return ctx_block.body

    def create_variable(
        self,
        name: t.Union[str, ast.Name],
        tags: t.Sequence[Tag],
    ) -> t.List[ast.stmt]:
        ctx_assign = self.create_subcontext(name)

        for tag in tags:
            ctx_assign.construct_tag(tag)

        ctx_assign.ensure_output_assigned()
        return ctx_assign.body

    def create_subcontext(self, name: t.Union[str, ast.Name, None] = None):
        if name is None:
            variable = self.output_variable
        else:
            variable = Variable(name)

        return BuildContext(
            output_variable=variable,
            template=self.template,
            layout=self.layout,
            css=self.css,
            rules=self.rules,
        )
