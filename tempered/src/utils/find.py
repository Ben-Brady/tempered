"This is a seperate file in order to generate custom types"
import typing_extensions as t

T = t.TypeVar("T", infer_variance=True)


def find(
    array: t.Iterable[t.Any], type: t.Type[T], condition: t.Callable[[T], bool]
) -> T:
    for item in array:
        if isinstance(item, type) and condition(item):
            return item

    raise ValueError("Item not found")
