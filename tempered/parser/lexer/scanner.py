from typing import Sequence, Self
import string
from array import array


class TextScanner:
    original: str
    position: int = 0

    html: array[str]
    _checkpoint: tuple[array[str], int]|None = None

    def __init__(self, html: str):
        self.original = html
        self.html = array("u")
        self.html.fromunicode(html[::-1])


    @property
    def has_text(self) -> bool:
        return len(self.html) != 0


    def checkpoint(self):
        self._checkpoint = self.html[:], self.position


    def restore(self):
        if self._checkpoint is None:
            raise RuntimeError("No checkpoint to restore from")

        self.html, self.position = self._checkpoint
        self._checkpoint = None


    def pop(self, length: int = 1) -> str:
        popped_text = ""
        for _ in range(length):
            popped_text += self.html.pop()

        self.position += length
        return popped_text


    def accept(self, text: str) -> bool:
        if not self.startswith(text):
            return False

        self.html = self.html[:-len(text)]
        self.position += len(text)
        return True


    def startswith(self, *text: str) -> bool:
        for match in text:
            html_text = self.html[-len(match)::][::-1].tounicode()
            if html_text == match:
                return True

        return False


    def expect(self, text: str):
        if not self.accept(text):
            raise self.error(f"Expected {text!r}")


    def take_until(self, matches: str|list[str]) -> str:
        if isinstance(matches, str):
            matches = [matches]

        text = ""
        while self.has_text:
            if self.startswith(*matches):
                break

            text += self.pop()

        return text

    def take_while(self, *matches: str) -> str:
        text = ""
        while self.has_text:
            if not self.startswith(*matches):
                break

            text += self.pop()

        return text


    def error(self, msg: str) -> Exception:
        return ParserException.create(msg, self.original, self.position)


class ParserException(Exception):
    @classmethod
    def create(cls, msg: str, source: str, position: int) -> Self:
        line_index = source[:position].count("\n") - 1

        lines = source.split("\n")

        err_line = lines[line_index]

        try:
            prev_line = "\n" + lines[line_index - 1]
        except IndexError:
            prev_line = ""

        try:
            next_line = "\n" + lines[line_index + 1]
        except IndexError:
            next_line = ""


        line_no = line_index + 1
        line_start = source.rfind("\n", 0, position) + 1
        offset = position - line_start

        message = (
            f"{msg} on line {line_no}, offset {offset}" +
            "\n" +
            prev_line +
            f"{err_line}\n" +
            f"{offset * ' '}^" +
            next_line
        )
        return cls(message)
