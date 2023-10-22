from markupsafe import escape_silent
from typing import Any

def escape(value: Any) -> str:
    return str(escape_silent(value))
