from __future__ import annotations
from scripts.app import PostType
from markupsafe import escape_silent as __escape_markup


def __escape(value: str) -> str:
    return str(__escape_markup(value))


def post() -> str:
    html = ''
    html += '{ param post: Post }\n\n\n'
    return html


def demo() -> str:
    html = ''
    html += 'div{color:red}'
    html += "<div style='display:contents;' id='2'>" + (html + '</div>')
    html += '<style>#2 div{color:red}</style>'
    html += """{!param a }
{!param b: str }
{!param c = 1 }
{!param d: int = "asd" }

{!for x in range(10) }
    {!if x % 2 == 0}
        <span>
            { x } is even
        </span>
    {!else}
        <span>
            { x } is odd
        </span>
    {!endif}
{!endfor}



"""
    return html
