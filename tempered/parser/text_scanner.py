from ..errors import ParserException
from typing_extensions import TYPE_CHECKING
from array import array
from pathlib import Path


class TextScanner:
    original: str
    position: int = 0
    file: Path | None

    if TYPE_CHECKING:
        text: array[str]
        _checkpoint: tuple[array[str], int] | None = None

    def __init__(self, html: str, file: Path | None = None):
        self.file = file
        self.original = html
        self.text = array("u")
        self.text.fromunicode(html[::-1])

    @property
    def has_text(self) -> bool:
        return len(self.text) != 0

    def checkpoint(self):
        self._checkpoint = self.text[:], self.position

    def backtrack(self):
        if self._checkpoint is None:
            raise RuntimeError("No checkpoint to backtrack to")

        self.text, self.position = self._checkpoint
        self._checkpoint = None

    def pop(
        self,
    ) -> str:
        return self.text.pop()

    def accept(self, *text: str) -> bool:
        for match in text:
            if not self.startswith(match):
                continue

            self.text = self.text[: -len(match)]
            self.position += len(match)
            return True

        return False

    def expect(self, text: str):
        if not self.accept(text):
            raise self.error(f"Expected {text!r}")

    def startswith(self, *text: str) -> bool:
        for match in text:
            prefix = self.text[-len(match) : :][::-1].tounicode()

            if prefix == match:
                return True

        return False

    def pop_many(self, length: int) -> str:
        if len(self.text) < length:
            self.error("Unexpected end of text")

        popped_text = ""
        for _ in range(length):
            popped_text += self.pop()

        self.position += length
        return popped_text

    def take_optional(self, *text: str) -> str | None:
        for match in text:
            if not self.startswith(match):
                continue

            self.expect(match)
            return match

        return None

    def take(self, *text: str) -> str:
        value = self.take_optional(*text)
        if value is None:
            raise self.error(f"Expected one of {','.join(text)}")

        return value

    def take_until(self, matches: str | list[str]) -> str:
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
        return ParserException.create(msg, self.file, self.original, self.position)
