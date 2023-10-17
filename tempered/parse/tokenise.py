from .tokens import *
from . import parse_ast
from ..ast_utils import create_constant,
from dataclasses import dataclass


def to_token_stream(html: str) -> list[TokenType]:
    return [
        ExprToken(value=create_constant(html))
    ]

