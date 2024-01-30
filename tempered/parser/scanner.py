from pathlib import Path
import typing_extensions as t
from ..errors import ParserException

TToken = t.TypeVar("TToken")


class Scanner(t.Generic[TToken]):
    stream: t.Sequence[TToken]

    def __init__(self, stream: t.Sequence[TToken]):
        self.stream = stream

    @property
    def has_tokens(self) -> bool:
        return len(self.stream) != 0

    def pop(self) -> TToken:
        popped = self.stream[0]
        self.stream = self.stream[1:]
        return popped

    def is_next(self, *token: t.Type[TToken]):
        if self.has_tokens and isinstance(self.stream[0], token):
            return True
        else:
            return False

    T = t.TypeVar("T")

    def accept(self, token: t.Type[T]) -> t.Optional[T]:
        if self.is_next(token):  # type: ignore
            return self.pop()  # type: ignore
        else:
            return None

    def peek(self) -> TToken:
        return self.stream[0]

    def expect(self, token: t.Type[T]) -> T:
        if not self.is_next(token):  # type: ignore
            raise ValueError(f"Expected {token} but got {self.stream[0]!r}")
        else:
            return self.pop()  # type: ignore


class TextScanner:
    original: str
    position: int = 0
    file: t.Union[Path, None]
    text: str

    def __init__(self, html: str, file: t.Union[Path, None] = None):
        self.file = file
        self.original = html
        self.text = html

    @property
    def has_text(self) -> bool:
        return len(self.text) != 0

    def pop(self) -> str:
        char = self.text[0]
        self.text = self.text[1:]
        return char

    def accept(self, text: str) -> bool:
        if not self.startswith(text):
            return False

        self.text = self.text[len(text) :]
        self.position += len(text)
        return True

    def expect(self, *text: str):
        match = ""
        for match in text:
            if self.accept(match):
                return

        raise self.error(f"Expected {match!r}")

    def startswith(self, text: str) -> bool:
        prefix = self.text[: len(text)]
        return prefix == text

    def startswith_many(self, *text: str) -> bool:
        for match in text:
            if self.startswith(match):
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

    def take_until(self, matches: t.Union[str, t.Sequence[str]]) -> str:
        if isinstance(matches, str):
            matches = [matches]

        text = ""
        while self.has_text:
            if self.startswith_many(*matches):
                break

            text += self.pop()

        return text

    def take_while(self, *matches: str) -> str:
        text = ""
        while self.has_text:
            if not self.startswith_many(*matches):
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
