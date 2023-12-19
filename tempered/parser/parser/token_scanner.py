from ..tokens import Token
import typing_extensions as t



class TokenScanner:
    stream: t.Sequence[Token]
    _checkpoint: t.Union[t.Sequence[Token], None] = None

    def __init__(self, stream: t.Sequence[Token]):
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

    def is_next(self, *token: t.Type[Token]):
        if len(self.stream) == 0:
            return False
        elif isinstance(self.stream[0], token):
            return True
        else:
            return False

    def accept(self, token: t.Type[Token]) -> bool:
        if self.is_next(token):
            self.pop()
            return True
        else:
            return False


    T = t.TypeVar("T", bound=Token)
    def expect(self, token: t.Type[T]) -> T:
        if not self.is_next(token):
            raise ValueError(f"Expected {token} but got {self.stream[0]!r}")
        else:
            return self.pop() # type: ignore

    T = t.TypeVar("T", bound=Token)
    def take_while(self, token: t.Type[T]) -> t.Sequence[T]:
        tokens = []
        while self.is_next(token):
            tokens.append(self.pop())

        return tokens

