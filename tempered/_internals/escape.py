from typing import Any
import sys

SAFE_CONVERSIONS = (int, float)

if sys.version_info <= (3, 9):
    def escape(value: Any) -> str:
        if type(value) in SAFE_CONVERSIONS:
            return str(value)

        return (
            str(value)
            .replace("&", "&amp;")
            .replace(">", "&gt;")
            .replace("<", "&lt;")
            .replace("'", "&#39;")
            .replace('"', "&#34;")
        )

else:
    from markupsafe import escape_silent

    def escape(value: Any) -> str:
        if type(value) in SAFE_CONVERSIONS:
            return str(value)

        return str(escape_silent(value))
