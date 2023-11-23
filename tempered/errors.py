from pathlib import Path
from typing_extensions import Self


class BuildError(Exception):
    pass


class ParsingWarning(Warning):
    pass


class InvalidTemplate(BuildError):
    @classmethod
    def create(
        cls,
        msg: str,
        name: str,
        file: Path | None,
    ) -> Self:
        if file:
            return cls(f"{msg} in {name} \n{file.absolute()}")
        else:
            return cls(f"{msg} in {name}")




class ParserException(BuildError):
    @classmethod
    def create(cls, msg: str, file: Path | None, source: str, position: int) -> Self:
        msg = create_parse_error_message(msg, file, source, position)
        return cls(msg)


def create_parse_error_message(
    msg: str, file: Path | None, source: str, position: int
) -> str:
    MAX_LINE_LENGTH = 80
    line_index = source[:position].count("\n")

    lines = source.split("\n")

    err_line = lines[line_index]

    try:
        prev_line = lines[line_index - 1]
        if len(prev_line) > MAX_LINE_LENGTH:
            prev_line = prev_line[:MAX_LINE_LENGTH] + "..."
    except IndexError:
        prev_line = ""

    try:
        next_line = lines[line_index + 1]
        if len(next_line) > MAX_LINE_LENGTH:
            next_line = next_line[:MAX_LINE_LENGTH] + "..."
    except IndexError:
        next_line = ""

    line_no = line_index + 1
    line_start = source.rfind("\n", 0, position) + 1
    offset = position - line_start

    if offset > MAX_LINE_LENGTH:
        cutoff = offset - MAX_LINE_LENGTH
        err_line = "..." + err_line[cutoff:]
        offset = MAX_LINE_LENGTH

    if file:
        msg = (
            f"{msg} in {file.name} on line {line_no}, offset {offset} \n"
            f"{file.absolute()}:{line_no}:{offset}"
        )
    else:
        msg = f"{msg} on line {line_no}, offset {offset}"

    return (
        msg + "\n" + prev_line + "\n" + err_line + "\n" + f"{offset * ' '}^"
        "\n" + next_line
    )
