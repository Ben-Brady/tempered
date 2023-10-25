from typing import Sequence
import string
from array import array


class TextScanner:
    html: array[str]
    _checkpoint: array[str]|None = None

    def __init__(self, html: str):
        self.html = array("u")
        self.html.fromunicode(html[::-1])


    @property
    def has_text(self) -> bool:
        return len(self.html) != 0


    def checkpoint(self):
        self._checkpoint = self.html[:]


    def restore(self):
        if self._checkpoint is None:
            raise RuntimeError("No checkpoint to restore from")

        self.html = self._checkpoint
        self._checkpoint = None


    def pop(self, length: int = 1) -> str:
        popped_text = ""
        for _ in range(length):
            popped_text += self.html.pop()

        return popped_text


    def startswith(self, *text: str) -> bool:
        for match in text:
            html_text = self.html[-len(match)::][::-1].tounicode()
            if html_text == match:
                return True

        return False


    def accept(self, text: str) -> bool:
        if not self.startswith(text):
            return False

        self.html = self.html[:-len(text)]
        return True


    def expect(self, text: str):
        if not self.accept(text):
            raise ValueError(f"Expected {text!r} but got {self.html!r}")


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

    def take_whitespace(self):
        WHITESPACE_CHARS = list(string.whitespace)
        self.take_while(*WHITESPACE_CHARS)


    def take_ident(self) -> str:
        IDENT_LETTERS = list(string.ascii_letters + string.digits + "_")
        return self.take_while(*IDENT_LETTERS)
