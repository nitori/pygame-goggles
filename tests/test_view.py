import math

import pytest
from pygame.typing import RectLike

from pygame_visor import Visor, VisorMode
from pygame_visor.types import ScreenPos, WorldPos


@pytest.mark.parametrize("initial_region,move_to,expected_region,expected_end", [
    [(0, 0, 100, 100), (50, 50), (0, 0, 100, 100), (100, 100)],
    [(0, 0, 100, 100), (10, 10), (-40, -40, 100, 100), (60, 60)],
    [(-50, -50, 100, 100), (0, 0), (-50, -50, 100, 100), (50, 50)],
    [(0.5, 0.5, 1.0, 1.0), (1.25, 1.25), (0.75, 0.75, 1.0, 1.0), (1.75, 1.75)],
])
def test_move_to(initial_region: RectLike, move_to: WorldPos, expected_region: RectLike, expected_end: WorldPos):
    """
    Region view modes have the same results.
    This mostly just test if the pygame rect move is applied correctly.
    No need to test the Rect itself.
    """
    for mode in (VisorMode.RegionLetterbox, VisorMode.RegionExpand):
        view = Visor(mode, initial_region=initial_region)
        view.move_to(move_to)
        assert tuple(view.region) == expected_region, f"Failed for {mode}"
        assert tuple(view.region.bottomright) == expected_end, f"Failed for {mode}"


@pytest.mark.parametrize("mode,initial_region,screen_rect,expected_bounding_box", [
    # the region stays exactly the same.
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (0, 0, 400, 300)],
    [VisorMode.RegionLetterbox, (0, 0, 100, 100), (1920, 1080), (0, 0, 100, 100)],

    # we get some extra view in the area outside the internal region
    [VisorMode.RegionExpand, (0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],

    [VisorMode.RegionExpand, (0, 0, 100, 100), (1920, 1080), (-39, 0, 178, 100)],
    [VisorMode.RegionExpand, (0, 0, 100, 100), (1080, 1920), (0, -39, 100, 178)],

    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (-67, 0, 534, 300)],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, -206, 400, 712)],

    [VisorMode.RegionExpand, (-549, 317, 400, 300), (1920, 1080), (-616, 317, 534, 300)],
    [VisorMode.RegionExpand, (-549, 317, 400, 300), (1080, 1920), (-549, 111, 400, 712)],
])
def test_bounding_box(mode: VisorMode, initial_region: RectLike, screen_rect: RectLike, expected_bounding_box: RectLike):
    view = Visor(mode, initial_region=initial_region)
    bounding_box = view.get_bounding_box(screen_rect)
    for a, b in zip(tuple(bounding_box), expected_bounding_box):
        assert math.isclose(a, b), f"Failed for {mode} with: {tuple(bounding_box)} == {expected_bounding_box}"


@pytest.mark.parametrize("initial_region,screen_rect,expected_factor", [
    [(0, 0, 400, 300), (400, 300), 1.0],
    [(0, 0, 400, 300), (1920, 1080), 3.6],
    [(0, 0, 800, 600), (400, 300), 0.5],
])
def test_scaling_factor(initial_region: RectLike, screen_rect: RectLike, expected_factor: float):
    view = Visor(VisorMode.RegionLetterbox, initial_region=initial_region)
    factor = view.get_scaling_factor(screen_rect)
    assert factor == expected_factor


@pytest.mark.parametrize("initial_region,screen_rect,expected_world_screen_rect", [
    [(0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],
    [(0, 0, 400, 300), (1920, 1080), (240, 0, 1440, 1080)],
    [(0, 0, 800, 600), (400, 300), (0, 0, 400, 300)],
    [(0, 0, 400, 300), (1080, 1920), (0, 555, 1080, 810)],
])
def test_region_screen_rect(initial_region: RectLike, screen_rect: RectLike, expected_world_screen_rect: RectLike):
    view = Visor(VisorMode.RegionLetterbox, initial_region=initial_region)
    world_screen_rect = view.get_region_screen_rect(screen_rect)
    for a, b in zip(world_screen_rect, expected_world_screen_rect):
        assert math.isclose(a, b), f"Failed for: {tuple(world_screen_rect)} == {expected_world_screen_rect}"


@pytest.mark.parametrize("mode,initial_region,screen_rect,screen_pos,expected_world_pos", [
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (200, 150), (200, 150)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (960, 540), (200, 150)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (384, 108), (40, 30)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (240, 0), (0, 0)],

    [VisorMode.RegionLetterbox, (100, 100, 400, 300), (400, 300), (200, 150), (300, 250)],

    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (1679, 1079),
     (400 / 1440 * 1439, 300 / 1080 * 1079)],

    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (1680, 1080), None],  # the ends are *exclusive*
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (1680, 1080), (400, 300)],

    # offset: (240, 0)
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (60, 0), None],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (60, 0), (-50, 0)],

    # offset: (0, 555)
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1080, 1920), (0, 420), None],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, 420), (0, -50)],
])
def test_screen_to_world(
    mode: VisorMode,
    initial_region: RectLike,
    screen_rect: RectLike,
    screen_pos: ScreenPos,
    expected_world_pos: WorldPos | None
):
    view = Visor(mode, initial_region=initial_region)
    world_pos = view.screen_to_world(screen_rect, screen_pos)
    if expected_world_pos is None or world_pos is None:
        assert world_pos == expected_world_pos
    else:
        for a, b in zip(world_pos, expected_world_pos):
            assert math.isclose(a, b), f"Failed for {mode} width: {tuple(world_pos)} == {expected_world_pos}"


@pytest.mark.parametrize("mode,initial_region,screen_rect,world_pos,expected_screen_pos", [
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (200, 150), (200, 150)],
    [VisorMode.RegionLetterbox, (100, 100, 400, 300), (400, 300), (300, 250), (200, 150)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (200, 150), (960, 540)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (40, 30), (384, 108)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (0, 0), (240, 0)],
    [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (400 / 1440 * 1439, 300 / 1080 * 1079), (1679, 1079)],

    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (0, 0), (240, 0)],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (400, 300), (1680, 1080)],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (400, 300), (1680, 1080)],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (-50, 0), (60, 0)],
    [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, -50), (0, 420)],
])
def test_world_to_screen(
    mode: VisorMode,
    initial_region: RectLike,
    screen_rect: RectLike,
    world_pos: WorldPos,
    expected_screen_pos: ScreenPos
):
    view = Visor(mode, initial_region=initial_region)
    screen_pos = view.world_to_screen(screen_rect, world_pos)

    for a, b in zip(screen_pos, expected_screen_pos):
        assert math.isclose(a, b), f"Failed for {mode} width: {tuple(screen_pos)} == {expected_screen_pos}"
