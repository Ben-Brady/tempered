from ..lexer import Token
from typing import Sequence


class TokenScanner:
    stream: Sequence[Token]
    _checkpoint: Sequence[Token]|None = None

    def __init__(self, stream: Sequence[Token]):
        self.stream = stream


    @property
    def has_tokens(self) -> bool:
        return len(self.stream) != 0


    def checkpoint(self):
        self._checkpoint = self.stream


    def restore(self):
        if self._checkpoint is None:
            raise RuntimeError("No checkpoint to restore from")

        self.stream = self._checkpoint
        self._checkpoint = None


    def pop(self) -> Token:
        popped = self.stream[0]
        self.stream = self.stream[1:]
        return popped

    def is_next(self, *token: type[Token]):
        if len(self.stream) == 0:
            return False
        elif isinstance(self.stream[0], token):
            return True
        else:
            return False

    def accept(self, token: type[Token]) -> bool:
        if self.is_next(token):
            self.pop()
            return True
        else:
            return False


    def expect[T: Token](self, token: type[T]) -> T:
        if not self.is_next(token):
            raise ValueError(f"Expected {token} but got {self.stream[0]!r}")
        else:
            return self.pop() # type: ignore


    def take_while[T: Token](self, token: type[T]) -> Sequence[T]:
        tokens = []
        while self.is_next(token):
            tokens.append(self.pop())

        return tokens

