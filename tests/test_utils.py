from typing import Type

import pytest
import pygame

from pygame_visor.utils import convert_to_vec


@pytest.mark.parametrize("tpl,expected_xy", [
    [(0, 0), (0.0, 0.0)],
    [(-1, -1), (-1.0, -1.0)],
    [pygame.Vector2(-10, 10), (-10.0, 10.0)],
])
def test_convert_to_vec(tpl, expected_xy):
    vec = convert_to_vec(tpl)  # noqa
    assert vec.xy == expected_xy


@pytest.mark.parametrize("value,expected_error", [
    [(), ValueError],
    [("",), ValueError],
    [("", ""), TypeError],
    [(0,), ValueError],
    [(0, 0, 0), ValueError],
    ["some_string", TypeError],
    [123, TypeError],
])
def test_convert_to_vec_error(value, expected_error: Type[BaseException]):
    with pytest.raises(expected_error):
        convert_to_vec(value)  # noqa
