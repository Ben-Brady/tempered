"Generate native python functions from HTML templates"
__version__ = "0.8.0"
from .tempered import Tempered as Tempered
from .enviroment import Environment as Environment, Template as Template
from . import errors as errors
from .errors import ParserException, InvalidTemplate, BuildError


__all__ = [
    "Tempered",
    "Environment",
    "Template",
    "errors",
    "ParserException",
    "InvalidTemplate",
    "BuildError",
]
