"Generate native python functions from HTML templates"
__version__ = "0.10.0"
from .src.errors import (
    InvalidTemplateException as InvalidTemplateException,
    ParserException as ParserException,
    ParsingWarning as ParsingWarning,
    BuildException as BuildException
)
from .src.tempered import Tempered as Tempered

__all__ = [
    "Tempered",
    "InvalidTemplateException",
    "ParserException",
    "ParsingWarning",
    "BuildException",
]
