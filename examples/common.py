from typing import Generator
import random

import pygame

SEED = 123


def generate_world_tiles(
    size: tuple[int, int],
    world_offset: tuple[int | float, int | float],
    tile_size: int
):
    """
    size in number of (rows, columns)
    offset in (x,y) world coordinates.
    tile_size integer of size in world coordinates.

    returns list of tile-tuples: (world_x, world_y, tile_surf)
    """

    random.seed(SEED)

    rows, columns = size
    off_x, off_y = world_offset

    tiles = []
    for row in range(rows):
        for column in range(columns):
            tone = random.randint(64, 240)
            tile = pygame.Surface((tile_size, tile_size))
            tile.fill((tone, 255, tone))
            tiles.append((off_x + row * tile_size, off_y + column * tile_size, tile))
    return tiles


def get_tiles_for_bbox(
    tiles: list[tuple[float, float, pygame.Surface]],
    bbox: pygame.FRect
) -> Generator[tuple[tuple[float, float], pygame.Surface]]:
    """
    Just look through all tiles, and look for the once we need.
    Terrible performance, but it should work for this example.
    """

    for x, y, surf in tiles:
        if surf.get_rect(topleft=(x, y)).colliderect(bbox):
            yield (x, y), surf


class App:
    def __init__(self, size: tuple[int, int] = (800, 600)):
        pygame.init()

        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.clock = pygame.Clock()

        self.rows = 50
        self.columns = 50
        self.tile_size = 32

        self.offset = (
            - (self.rows * self.tile_size) / 2,
            - (self.columns * self.tile_size) / 2,
        )

        self.tiles = generate_world_tiles((self.rows, self.columns), self.offset, self.tile_size)

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
        self.player_pos = self.player_surf.get_rect(center=(200, 150))

    def extended_limits(self, value):
        return [
            self.limits[0] - value,
            self.limits[1] - value,
            self.limits[2] + value,
            self.limits[3] + value,
        ]

    def loop(self, callback=None):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if callback:
                    callback(event)

            delta = self.clock.tick(60) / 1000

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

            pygame.display.flip()
