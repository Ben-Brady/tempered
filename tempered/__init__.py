"Generate native python functions from HTML templates"
__version__ = "0.6.4"
from .tempered import Tempered
from . import errors


__all__ = [
    "Tempered",
    "errors",
]
