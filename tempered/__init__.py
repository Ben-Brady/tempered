"Generate native python functions from HTML templates"
__version__ = "0.7.3"
from .tempered import Tempered
from . import errors


__all__ = [
    "Tempered",
    "errors",
]
