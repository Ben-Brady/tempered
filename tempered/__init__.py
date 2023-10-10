"Generate native python functions from HTML templates"
__version__ = "0.0.1"
from .main import add_template, add_template_folder, build, register_type

__all__ = [
    "add_template",
    "add_template_folder",
    "build",
]
