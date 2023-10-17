"Generate native python functions from HTML templates"
__version__ = "0.0.2"
from .main import (
    add_template, add_template_obj, add_template_folder,
    register_type, build, load,
)

__all__ = [
    "add_template",
    "add_template_obj",
    "add_template_folder",
    "register_type",
    "build",
    "load",
]
