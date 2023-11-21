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

    str_text = _take_string(
        scanner,
        terminator=terminator,
        is_multiline=is_multiline,
        is_bytestring=is_bytestring,
    )
    return prefix + terminator + str_text + terminator


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


def take_number(scanner: TextScanner) -> str:
    DEC_DIGITS = "_" + "0123456789"
    BIN_DIGITS = "_" + "01"
    OCT_DIGITS = "_" + "01234567"
    HEX_DIGITS = "_" + "0123456789" + "abcdef" + "ABCDEF"

    if not scanner.startswith("0"):
        return scanner.take_while(DEC_DIGITS)

    scanner.expect("0")
    if scanner.accept("b") or scanner.accept("B"):
        return "0b" + scanner.take_while(*BIN_DIGITS)
    elif scanner.accept("o") or scanner.accept("O"):
        return "0o" + scanner.take_while(*OCT_DIGITS)
    elif scanner.accept("x") or scanner.accept("X"):
        return "0x" + scanner.take_while(*HEX_DIGITS)
    else:
        return scanner.take_while(*"0_")

def take_value(scanner: TextScanner) -> str:
    stack = []
    text = ""

    while len(stack) != 0:
        if scanner.accept("None"):
            text += "None"
        elif scanner.accept("True"):
            text += "True"
        elif scanner.accept("False"):
            text += "False"
        elif scanner.startswith("'", '"'):
            return take_string(scanner)
        elif scanner.startswith(*string.digits):
            return take_number(scanner)
        elif scanner.startswith(*IDENT_START):
            return take_ident(scanner)
        elif scanner.startswith("{", "[", "("):
            char = scanner.pop()
            stack.append(char)
            text += char
        elif scanner.startswith("}", "]", ")"):
            stack.pop()
            text += scanner.pop()

        if not scanner.has_text:
            break

    return text
