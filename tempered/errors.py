from __future__ import annotations
from pathlib import Path
import typing_extensions as t
from dataclasses import dataclass
import sys


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
        file: t.Union[Path, None],
    ) -> t.Self:
        if file:
            return cls(f"{msg} in {name} \n{file.absolute()}")
        else:
            return cls(f"{msg} in {name}")


class ParserException(BuildError):
    error_info: ErrorInfo | None = None

    @classmethod
    def create(
        cls,
        msg: str,
        source: str,
        file: t.Union[Path, None],
    ) -> t.Self:
        line_no, offset = calculate_line_and_offset(source, position)
        err_info = ErrorInfo(
            msg=msg,
            file=file,
            source=source,
            line_no=line_no,
            offset=offset,
        )
        return cls(create_error_message(err_info))

    @classmethod
    def create_from_parser(
        cls,
        msg: str,
        source: str,
        position: int,
        file: t.Union[Path, None],
    ) -> t.Self:
        line_no, offset = calculate_line_and_offset(source, position)
        err_info = ErrorInfo(
            msg=msg,
            file=file,
            source=source,
            line_no=line_no,
            offset=offset,
        )
        msg = "\n".join(
            (
                create_error_message(err_info),
                err_info.prev_line or "",
                err_info.err_line,
                f"{' ' * err_info.offset}^",
                err_info.next_line or "",
            )
        )

        err = cls(msg)
        err.error_info = err_info
        return err


def create_error_message(file: ErrorInfo) -> str:
    if info.file:
        return (
            f"{info.msg} in {file.name} on line {info.line_no}, offset {info.offset} \n"
            f"{info.file.absolute()}:{info.line_no}:{info.offset}"
        )
    else:
        return f"{info.msg} on line {info.line_no}, offset {info.offset}"


@dataclass
class ErrorInfo:
    file: t.Optional[Path]
    msg: str
    source: str
    line_no: int
    offset: int

    @property
    def lines(self) -> list[str]:
        return self.source.split("\n")

    @property
    def err_line(self) -> str:
        line_index = self.line_no - 1
        return self.lines[line_index]

    @property
    def prev_line(self) -> t.Union[str, None]:
        line_index = self.line_no - 1
        try:
            return self.lines[line_index - 1]
        except KeyError:
            return None

    @property
    def next_line(self) -> t.Union[str, None]:
        line_index = self.line_no - 1
        try:
            return self.lines[line_index + 1]
        except KeyError:
            return None


def calculate_line_and_offset(source: str, position: int) -> t.Tuple[int, int]:
    line_index = source[:position].count("\n")
    line_no = line_index + 1

    line_start = source.rfind("\n", 0, position) + 1  # + 1 for removed newline
    offset = position - line_start
    return line_no, offset
