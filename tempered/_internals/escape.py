from markupsafe import escape_silent
from typing import Any
from functools import lru_cache


@lru_cache(maxsize=1024, typed=True)
def escape(value: Any) -> str:
    return str(escape_silent(value))
