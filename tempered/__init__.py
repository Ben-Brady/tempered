"Generate native python functions from HTML templates"
__version__ = "0.10.0"
from .src.errors import (
    InvalidTemplate as InvalidTemplate,
    ParserException as ParserException,
    ParsingWarning as ParsingWarning,
    BuildError as BuildError,
    ErrorInfo as ErrorInfo
)
from .src.tempered import Tempered as Tempered

__all__ = [
    "Tempered",
    "InvalidTemplate",
    "ParserException",
    "ParsingWarning",
    "BuildError",
    "ErrorInfo",
]
