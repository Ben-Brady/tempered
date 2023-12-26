from ..errors import ParserException
import typing_extensions as t
from array import array
import sys
from pathlib import Path


class TextScanner:
    original: str
    position: int = 0
    file: t.Union[Path, None]

    if t.TYPE_CHECKING:
        text: array[str]
        _checkpoint: t.Union[t.Tuple[array[str], int], None] = None

    def __init__(self, html: str, file: t.Union[Path, None] = None):
        self.file = file
        self.original = html
        if sys.version_info >= (3, 13):
            self.text = array("w", html[::-1])
        else:
            self.text = array("u", html[::-1])

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

    def take_optional(self, *text: str) -> t.Union[str, None]:
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

    def take_until(self, matches: t.Union[str, t.List[str]]) -> str:
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
        return ParserException.create_from_parser(
            msg=msg,
            file=self.file,
            source=self.original,
            position=self.position,
        )
