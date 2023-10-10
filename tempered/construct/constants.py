import ast

ESCAPE_FUNC_NAME = ast.Name(id='__escape', ctx=ast.Load())

ANNOTATIONS_IMPORT = ast.ImportFrom(
    module='__future__',
    names=[ast.alias(name='annotations')],
    level=0,
)

MARKUPSAFE_ESCAPE_NAME = ast.Name(id='__escape_markup', ctx=ast.Load())
MARKUPSAFE_IMPORT = ast.ImportFrom(
    module='markupsafe',
    names=[ast.alias(name='escape_silent', asname=MARKUPSAFE_ESCAPE_NAME.id)],
    level=0,
)

ESCAPE_FUNC = ast.FunctionDef(
    name="__escape",
    args=ast.arguments(
        posonlyargs=[],
        args=[
            ast.arg(
                arg="value",
                annotation=ast.Name(id="str", ctx=ast.Load())
            )
        ],
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[],
    ),
    body=[
        ast.Return(
            value=ast.Call(
                func=ast.Name(id="str", ctx=ast.Load()),
                args=[
                    ast.Call(
                        func=MARKUPSAFE_ESCAPE_NAME,
                        args=[ast.Name(id="value", ctx=ast.Load())],
                        keywords=[],
                    )
                ],
                keywords=[],
            )
        )
    ],
    returns=ast.Name(id='str', ctx=ast.Load()),
    decorator_list=[],
    type_params=[],
)
