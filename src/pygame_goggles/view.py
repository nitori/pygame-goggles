from typing import TypeGuard, reveal_type
from enum import Enum, auto
import math

import pygame
from pygame import FRect
from pygame.typing import RectLike

from .utils import convert_to_vec
from .types import WorldPos, ScreenPos, ScreenSize, ScreenRect, is_screen_rect, is_screen_size, SurfaceIterable

__all__ = ['ViewMode', 'View']


class ViewMode(Enum):
    RegionLetterbox = auto()
    RegionExpand = auto()


class View:
    mode: ViewMode
    region: FRect

    def __init__(self, mode: ViewMode, *, initial_region: RectLike) -> None:
        self.mode = mode
        self.region = FRect(initial_region)

    def move_to(self, pos: WorldPos) -> None:
        pos = convert_to_vec(pos)
        self.region.center = pos.x, pos.y

    @staticmethod
    def _screen_size(screen_rect: ScreenRect) -> ScreenSize:
        if is_screen_rect(screen_rect):
            sx, sy, sw, sh = screen_rect
            if (sx, sy) != (0, 0):
                raise ValueError("Screen rects must start at x=0, y=0")
            return sw, sh
        elif is_screen_size(screen_rect):
            sw, sh = screen_rect
            return sw, sh
        else:
            raise ValueError(f'screen_rect does not have a valid size of 2 or 4: {len(screen_rect)}')

    def get_bounding_box(self, screen_rect: ScreenRect) -> FRect:
        """
        Return the world region that needs to be rendered for display.
        """
        sw, sh = self._screen_size(screen_rect)

        if self.mode == ViewMode.RegionLetterbox:
            # the region to render is exactly the current region stored
            return FRect(self.region)

        # we need a bit more, depending on the size of the screen
        screen_ratio = sw / sh
        region_ratio = self.region.width / self.region.height

        if screen_ratio > region_ratio:
            # screen is wider
            new_width = math.ceil(self.region.height * screen_ratio)
            extra_width = new_width - self.region.width
            return FRect(
                self.region.x - (extra_width // 2),
                self.region.y,
                new_width,
                self.region.height,
            )

        # screen is higher
        new_height = math.ceil(self.region.width / screen_ratio)
        extra_height = new_height - self.region.height
        return FRect(
            self.region.x,
            self.region.y - (extra_height // 2),
            self.region.width,
            new_height,
        )

    def _get_scaling_factor(self, screen_rect: ScreenRect) -> float:
        sw, sh = self._screen_size(screen_rect)
        screen_ratio = sw / sh
        region_ratio = self.region.width / self.region.height

        if screen_ratio > region_ratio:
            return sh / self.region.height
        return sw / self.region.width

    def _get_region_screen_rect(self, screen_rect: ScreenRect) -> pygame.Rect:
        """Return where the region (top left) starts, irrespective of the mode."""
        factor = self._get_scaling_factor(screen_rect)
        sw, sh = self._screen_size(screen_rect)

        # world-screen width/height
        ws_width = self.region.width * factor
        ws_height = self.region.height * factor

        left = (sw - ws_width) // 2
        top = (sh - ws_height) // 2

        return pygame.Rect(left, top, ws_width, ws_height)

    def screen_to_world(self, screen_rect: ScreenRect, screen_pos: ScreenPos) -> pygame.Vector2 | None:
        """May return None in RegionLetterbox, if the pos is outside the bounding box"""
        # ViewMode.RegionLetterbox
        # region = (0, 0, 400, 300)
        # screen_rect = (0, 0, 1920, 1080)   -- region scaled to: (1440, 1080)
        # pos = (384, 108)                   -- 240 + 144  (240 padding + 10% of 1440; 10% of 1080)
        # expected world_pos = (40, 30)      -- (10% of 400; 10% of 300)

        sx, sy = screen_pos
        factor = self._get_scaling_factor(screen_rect)
        ws_x, ws_y, _, _ = self._get_region_screen_rect(screen_rect)

        wx = (sx - ws_x) / factor + self.region.x
        wy = (sy - ws_y) / factor + self.region.y

        if self.mode == ViewMode.RegionLetterbox:
            if self.region.x <= wx < self.region.width \
                and self.region.y <= wy < self.region.height:
                return pygame.Vector2(wx, wy)
            return None

        return pygame.Vector2(wx, wy)

    def world_to_screen(self, screen_rect: ScreenRect, world_pos: WorldPos) -> ScreenPos:
        # ViewMode.RegionLetterbox
        # region = (0, 0, 400, 300)
        # screen_rect = (0, 0, 1920, 1080)   -- region scaled to: (1440, 1080)
        # world_pos = (40, 30)               -- (10% of 400; 10% of 300)
        # expected screen_pos = (384, 108)   -- 240 + 144  (240 padding + 10% of 1440; 10% of 1080)

        wx, wy = world_pos
        factor = self._get_scaling_factor(screen_rect)
        ws_x, ws_y, _, _ = self._get_region_screen_rect(screen_rect)

        sx = int((wx - self.region.x) * factor + ws_x)
        sy = int((wy - self.region.y) * factor + ws_y)

        return sx, sy

    def render(self, surface: pygame.Surface, surface_iterable: SurfaceIterable, *, debug: bool = False) -> None:
        screen_rect = surface.get_rect()
        factor = self._get_scaling_factor(screen_rect)
        draw_area = self._get_region_screen_rect(screen_rect)
        subsurface = surface.subsurface(draw_area)

        for world_xy, surf in surface_iterable:
            if not math.isclose(factor, 1.0):
                surf = pygame.transform.scale_by(surf, factor)
            sx, sy = self.world_to_screen(screen_rect, world_xy)
            sx -= draw_area.x
            sy -= draw_area.y
            subsurface.blit(surf, (sx, sy))
