from typing import Sequence
import string


# Try using array.array
class TextScanner:
    html: str
    _checkpoint: str|None = None

    def __init__(self, html: str):
        self.html = html


    @property
    def has_text(self) -> bool:
        return len(self.html) != 0


    def checkpoint(self):
        self._checkpoint = self.html


    def restore(self):
        if self._checkpoint is None:
            raise RuntimeError("No checkpoint to restore from")

        self.html = self._checkpoint
        self._checkpoint = None


    def pop(self, length: int = 1) -> str:
        popped_text = self.html[:length]
        self.html = self.html[length:]
        return popped_text


    def startswith(self, *text: str) -> bool:
        return any((
            self.html.startswith(match)
            for match in text
        ))


    def accept(self, text: str) -> bool:
        if not self.html.startswith(text):
            return False

        self.html = self.html[len(text):]
        return True


    def expect(self, text: str):
        if not self.accept(text):
            raise ValueError(f"Expected {text!r} but got {self.html!r}")


    def take_until(self, matches: str|list[str]) -> str:
        if isinstance(matches, str):
            matches = [matches]

        text = ""
        while self.has_text:
            if any(self.startswith(match) for match in matches):
                break

            text += self.pop(1)

        return text


    def take_while(self, *matches: str) -> str:
        text = ""
        while self.has_text:
            if not any(self.startswith(match) for match in matches):
                break

            text += self.pop(1)

        return text


    def take_whitespace(self):
        WHITESPACE_CHARS = list(string.whitespace)
        self.take_while(*WHITESPACE_CHARS)


    def take_ident(self) -> str:
        IDENT_LETTERS = list(string.ascii_letters + string.digits + "_")
        return self.take_while(*IDENT_LETTERS)

