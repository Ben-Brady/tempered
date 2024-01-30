"Generate native python functions from HTML templates"
__version__ = "0.9.2"
from . import errors as errors
from .tempered import Tempered as Tempered

__all__ = [
    "Tempered",
    "errors",
]
