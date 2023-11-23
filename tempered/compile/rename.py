import ast

def convert_unknown_variables_to_kwargs(body: list[ast.stmt], known_names: list[str]):
    class NameTransformer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name):
            return transform(node)

    def transform(node: ast.Name) -> ast.expr:
        if any((
            node.id == "kwargs",
            node.id.startswith("__"),
            node.id in dir(__builtins__),
            node.id in known_names,
        )):
            return node

        return ast.Subscript(
            value=ast.Name(id="kwargs", ctx=ast.Load()),
            slice=ast.Constant(value=node.id),
            ctx=node.ctx,
        )


    transformer = NameTransformer()
    for node in body:
        transformer.visit(node)
