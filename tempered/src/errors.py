from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import typing_extensions as t


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
    error_info: t.Optional[ErrorInfo] = None

    @classmethod
    def create(
        cls,
        msg: str,
        file: t.Union[Path, None],
    ) -> t.Self:
        if file:
            msg = f"{msg} in {file.name}"

        return cls(msg)

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
                err_info.create_error_message(),
                err_info.prev_line or "",
                err_info.err_line,
                f"{' ' * err_info.offset}^",
                err_info.next_line or "",
            )
        )

        err = cls(msg)
        err.error_info = err_info
        return err


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

    def create_error_message(self) -> str:
        if self.file:
            return (
                f"{self.msg} in {self.file.name} on line {self.line_no}, offset {self.offset} \n"
                f"{self.file.absolute()}:{self.line_no}:{self.offset}"
            )
        else:
            return f"{self.msg} on line {self.line_no}, offset {self.offset}"


def calculate_line_and_offset(source: str, position: int) -> t.Tuple[int, int]:
    line_index = source[:position].count("\n")
    line_no = line_index + 1

    line_start = source.rfind("\n", 0, position) + 1  # + 1 for removed newline
    offset = position - line_start
    return line_no, offset
