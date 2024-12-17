"This module is used internally by tempered for components"

from .escape import escape
from ..src.parsing import Template

__all__ = [
    "escape",
    "Template"
]
