from pygame import Vector2

from .types import WorldPos, WorldSize

type _PosSize = WorldPos | WorldSize


def convert_to_vec(value: _PosSize) -> Vector2:
    if isinstance(value, Vector2):
        return value
    elif isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("Invalid length of tuple for vector conversion.")
        try:
            return Vector2(*value)
        except ValueError as e:
            raise TypeError(f"The value must be of type {_PosSize.__value__}. Got {type(value)} instead.") from e
    raise TypeError(f"The value must be of type {_PosSize.__value__}. Got {type(value)} instead.")
