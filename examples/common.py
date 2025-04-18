"""
common.py – Shared helper code for pygame-visor examples.

This module provides a minimal application framework and utility functions
used across multiple examples. It handles basic Pygame setup, player movement,
world tile generation, and tile fetching based on a visible region.

Not intended for production use—just a simple, reusable base to keep example
code focused on demonstrating viewport/camera functionality.
"""

from typing import Generator
import random

import pygame

from pygame_visor.types import WorldPos

SEED = 123

type TileTuple = tuple[float, float, pygame.Surface]
type TileIndex = tuple[int, int]  # index as (column, row) pair
type Tiles = dict[TileIndex, TileTuple]


class App:
    tiles: Tiles

    def __init__(self, size: tuple[int, int] = (800, 600)):
        pygame.init()

        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.clock = pygame.Clock()

        self.rows = 150
        self.columns = 150
        self.tile_size = 32

        self.offset = (
            - (self.rows * self.tile_size) / 2,
            - (self.columns * self.tile_size) / 2,
        )

        self.tiles = self.generate_world_tiles()

        self.limits = [
            self.offset[0],
            self.offset[1],
            self.offset[0] + self.columns * self.tile_size,
            self.offset[1] + self.rows * self.tile_size,
        ]

        self.speed = 200

        # world size
        self.player_surf = pygame.Surface((10, 10))
        self.player_surf.fill('red')

        # world pos
        self.player_pos = self.player_surf.get_rect(center=(0, 0))

    def generate_world_tiles(self) -> Tiles:
        """
        size in number of (rows, columns)
        offset in (x,y) world coordinates.
        tile_size integer of size in world coordinates.

        returns list of tile-tuples: (world_x, world_y, tile_surf)
        """

        random.seed(SEED)

        off_x, off_y = self.offset

        tiles = {}
        for row in range(self.rows):
            for column in range(self.columns):
                tone = random.randint(64, 240)
                tile = pygame.Surface((self.tile_size, self.tile_size))
                tile.fill((tone, 255, tone))
                tiles[(column, row)] = (off_x + column * self.tile_size, off_y + row * self.tile_size, tile)
        return tiles

    def get_tiles_for_bbox(
        self,
        tiles: Tiles,
        bbox: pygame.FRect
    ) -> Generator[tuple[tuple[float, float], pygame.Surface]]:
        left_column, top_row = self.get_tile(bbox.topleft)
        right_column, bottom_row = self.get_tile(bbox.bottomright)

        # Some debugging left here
        # size_x = right_column - left_column + 1
        # size_y = bottom_row - top_row + 1
        # print(f'Requesting {size_x * size_y} tiles.')

        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                if data := tiles.get((column, row)):
                    x, y, surf = data
                    yield (x, y), surf

    def get_tile(self, pos: WorldPos) -> TileIndex:
        x, y = map(int, pos)
        column = int(x - self.offset[0]) // self.tile_size
        row = int(y - self.offset[1]) // self.tile_size
        return column, row

    def extended_limits(self, value):
        return [
            self.limits[0] - value,
            self.limits[1] - value,
            self.limits[2] + value,
            self.limits[3] + value,
        ]

    def loop(self, fps: int, callback=None):
        frames = 0
        acc_deltas = 0
        font = pygame.Font(pygame.font.get_default_font())
        fps_surf = font.render(f'FPS: {frames}', True, 'white', 'black')

        while True:
            frames += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if callback:
                    callback(event)

            delta = self.clock.tick(fps) / 1000

            keys = pygame.key.get_pressed()
            direction = pygame.Vector2(
                keys[pygame.K_d] - keys[pygame.K_a],
                keys[pygame.K_s] - keys[pygame.K_w],
            )

            if direction.length() > 0:
                direction.normalize_ip()
                self.player_pos.center += direction * self.speed * delta

            self.screen.fill('black')

            yield delta

            acc_deltas += delta
            if acc_deltas > 1.0:
                acc_deltas -= 1.0
                fps_surf = font.render(f'FPS: {frames}', True, 'white', 'black')
                frames = 0

            self.screen.blit(fps_surf, (10, 50))

            pygame.display.flip()
