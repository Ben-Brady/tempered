from markupsafe import escape_silent
from typing import Any
from functools import lru_cache


@lru_cache(maxsize=10_000)
def escape(value: Any) -> str:
    return str(escape_silent(value))
