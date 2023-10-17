from markupsafe import escape_silent

def escape(value: str) -> str:
    return str(escape_silent(value))
