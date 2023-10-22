"Generate native python functions from HTML templates"
__version__ = "0.3.0"
from .main import (
    add_template, add_template_folder, register_type,
    build, build_to, build_static,
)

__all__ = [
    "add_template", "add_template_folder", "register_type",
    "build", "build_to", "build_static",
]
