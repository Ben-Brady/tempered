from functools import lru_cache as __lru_cache, wraps
from typing import TypeVar, ParamSpec, Concatenate, Callable

ParamT = ParamSpec("ParamT")
ReturnT = TypeVar("ReturnT")


def template_cache(func: Callable[ParamT, ReturnT]) -> Callable[ParamT, ReturnT]:
    # _cached_func = __lru_cache(maxsize=1024, typed=True)(func)

    # @wraps(func)
    # def wrapper(*args: ParamT.args, **kwargs: ParamT.kwargs) -> ReturnT:
    #     try:
    #         return _cached_func(*args, **kwargs)
    #     except Exception:
    #         return func(*args, **kwargs)

    # return wrapper
    return func
