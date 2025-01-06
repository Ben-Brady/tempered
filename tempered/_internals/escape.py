from typing import Any

SAFE_CONVERSIONS = (int, float)


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
