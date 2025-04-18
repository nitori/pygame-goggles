from enum import Enum, auto
import math

import pygame
from pygame import FRect
from pygame.typing import RectLike

from .types import WorldPos, ScreenPos, ScreenSize, ScreenRect, is_screen_rect, is_screen_size, Limits, SurfaceIterable

__all__ = ['VisorMode', 'Visor']


class VisorMode(Enum):
    RegionLetterbox = auto()
    RegionExpand = auto()


class Visor:
    mode: VisorMode
    region: FRect
    limits: Limits | None

    def __init__(self, mode: VisorMode, *, initial_region: RectLike, limits: Limits | None = None) -> None:
        self.mode = mode
        self.region = FRect(initial_region)
        self.limits = limits

    def lerp_to(self, pos: WorldPos, weight: float = 1.0) -> None:
        px, py = pos
        cx, cy = self.region.center
        x = pygame.math.lerp(cx, px, weight)
        y = pygame.math.lerp(cy, py, weight)
        self.move_to((x, y))

    def move_to(self, pos: WorldPos) -> None:
        self.region.center = pos[0], pos[1]
        if self.limits is None:
            return

        lx1, ly1, lx2, ly2 = self.limits

        x1, y1 = self.region.topleft
        x1 = max(x1, lx1)
        y1 = max(y1, ly1)
        self.region.topleft = x1, y1

        x2, y2 = self.region.bottomright
        x2 = min(x2, lx2)
        y2 = min(y2, ly2)
        self.region.bottomright = x2, y2

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

        if self.mode == VisorMode.RegionLetterbox:
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

    def get_scaling_factor(self, screen_rect: ScreenRect) -> float:
        sw, sh = self._screen_size(screen_rect)
        screen_ratio = sw / sh
        region_ratio = self.region.width / self.region.height

        if screen_ratio > region_ratio:
            return sh / self.region.height
        return sw / self.region.width

    def scale_surf(self, screen_rect: ScreenRect, surface: pygame.Surface) -> pygame.Surface:
        factor = self.get_scaling_factor(screen_rect)
        return pygame.transform.scale_by(surface, factor)

    def get_region_screen_rect(self, screen_rect: ScreenRect) -> pygame.Rect:
        """
        Returns a screen rect of the world region translated to the screen, excluding
        any extended areas (doesn't consider ViewMode for calculcatio).
        This is so we can place UI or similar within that area.
        """
        factor = self.get_scaling_factor(screen_rect)
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
        factor = self.get_scaling_factor(screen_rect)
        ws_x, ws_y, _, _ = self.get_region_screen_rect(screen_rect)

        wx = (sx - ws_x) / factor + self.region.x
        wy = (sy - ws_y) / factor + self.region.y

        if self.mode == VisorMode.RegionLetterbox:
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
        factor = self.get_scaling_factor(screen_rect)
        ws_x, ws_y, _, _ = self.get_region_screen_rect(screen_rect)

        sx = int((wx - self.region.x) * factor + ws_x)
        sy = int((wy - self.region.y) * factor + ws_y)

        return sx, sy

    def render(self, surface: pygame.Surface, surface_iterable: SurfaceIterable, *, debug: bool = False) -> None:
        screen_rect = surface.get_rect()
        factor = self.get_scaling_factor(screen_rect)
        draw_area = self.get_region_screen_rect(screen_rect)
        if self.mode == VisorMode.RegionLetterbox:
            subsurface = surface.subsurface(draw_area)
        else:
            subsurface = surface

        for world_xy, surf in surface_iterable:
            if not math.isclose(factor, 1.0):
                w = math.ceil(surf.get_width() * factor)
                h = math.ceil(surf.get_height() * factor)
                surf = pygame.transform.scale(surf, (w, h))
            sx, sy = self.world_to_screen(screen_rect, world_xy)
            if self.mode == VisorMode.RegionLetterbox:
                sx -= draw_area.x
                sy -= draw_area.y
            subsurface.blit(surf, (sx, sy))
