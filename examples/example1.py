from typing import Generator
import random

import pygame

from pygame_goggles import View, ViewMode

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


def main():
    pygame.init()

    rows = 30
    columns = 30
    tile_size = 32

    offset = (
        - (rows * tile_size) / 2,
        - (columns * tile_size) / 2,
    )

    tiles = generate_world_tiles((rows, columns), offset, tile_size)

    limit_x1 = offset[0] - 10
    limit_y1 = offset[1] - 10

    limit_x2 = limit_x1 + columns * tile_size + 20
    limit_y2 = limit_y1 + rows * tile_size + 20

    screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)
    clock = pygame.Clock()

    view = View(
        ViewMode.RegionLetterbox,
        initial_region=(0, 0, 400, 300),
        limits=(limit_x1, limit_y1, limit_x2, limit_y2),
    )

    speed = 200

    # world size
    player_surf = pygame.Surface((10, 10))
    player_surf.fill('red')

    # world pos
    player_pos = player_surf.get_rect(center=(200, 150))
    view.move_to(player_pos.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        delta = clock.tick(60) / 1000

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w],
        )

        if direction.length() > 0:
            direction.normalize_ip()
            player_pos.center += direction * speed * delta

        screen.fill('black')

        view.move_to(player_pos.center)
        bbox = view.get_bounding_box(screen.get_rect())
        view.render(screen, get_tiles_for_bbox(tiles, bbox))
        view.render(screen, [
            (player_pos.topleft, player_surf)
        ])

        pygame.display.flip()


if __name__ == '__main__':
    main()
