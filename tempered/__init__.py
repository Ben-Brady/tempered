"Generate native python functions from HTML templates"
__version__ = "0.7.9"
from .tempered import Tempered as Tempered
from . import errors as errors
from .errors import ParserException, InvalidTemplate, BuildError


__all__ = [
    "Tempered",
    "errors",
    "ParserException",
    "InvalidTemplate",
    "BuildError",
]
