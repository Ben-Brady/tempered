from .text_scanner import TextScanner
import string


WHITESPACE = string.whitespace


IDENT_START = string.ascii_letters + "_"
IDENT_CONTINUE = IDENT_START
def take_ident(scanner: TextScanner) -> str:
    ident = scanner.take(*IDENT_START)
    ident += scanner.take_while(*IDENT_CONTINUE)
    return ident


def take_string(scanner: TextScanner) -> str:
    STRING_PREFIXES = (
        "r", "u", "R", "U", "f", "F",
        "fr", "Fr", "fR", "FR", "rf", "rF", "Rf", "RF"
    )
    BYTE_PREFIXES = "b", "B", "br", "Br", "bR", "BR", "rb", "rB", "Rb", "RB"
    SINGLELINE_TERMINATORS = ("'", '"')
    MULTILINE_TERMINATORS = ("'''", '"""')
    STRING_TERMINATORS = SINGLELINE_TERMINATORS + MULTILINE_TERMINATORS

    is_bytestring = scanner.startswith(*BYTE_PREFIXES)

    if is_bytestring:
        prefix = scanner.take(*BYTE_PREFIXES)
    else:
        prefix = scanner.take_optional(*STRING_PREFIXES) or ""

    terminator = scanner.take(*STRING_TERMINATORS)
    is_multiline = terminator in MULTILINE_TERMINATORS

    body = _take_string(
        scanner,
        terminator=terminator,
        is_multiline=is_multiline,
        is_bytestring=is_bytestring,
    )
    return prefix + terminator + body + terminator


def _take_string(
    scanner: TextScanner,
    terminator: str,
    is_multiline: bool,
    is_bytestring: bool,
    ):
    STRING_ESCAPE = "\\"

    text = ""

    while scanner.has_text:
        if scanner.startswith(terminator):
            scanner.expect(terminator)
            return text

        if scanner.startswith("\n") and not is_multiline:
            raise scanner.error("Newline in the middle of the string")

        if scanner.startswith(STRING_ESCAPE):
            text += STRING_ESCAPE

        char = scanner.pop()
        if not char.isascii() and is_bytestring:
            scanner.error("Non-ascii character in bytestring")

        text += char


    raise scanner.error("String was not closed")
