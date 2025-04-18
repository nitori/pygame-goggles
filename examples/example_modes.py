import pygame

from pygame_goggles import View, ViewMode
from common import App, get_tiles_for_bbox


def main():
    app = App()

    view1 = View(
        ViewMode.RegionLetterbox,
        initial_region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )
    view2 = View(
        ViewMode.RegionExpand,
        initial_region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    surf1 = pygame.Surface((app.screen.width, app.screen.height // 2))
    surf2 = pygame.Surface((app.screen.width, app.screen.height // 2))

    view1.move_to(app.player_pos.center)
    view2.move_to(app.player_pos.center)

    font = pygame.font.Font(pygame.font.get_default_font())
    text1 = font.render(f"{view1.mode}", True, 'black', 'white')
    text2 = font.render(f"{view2.mode}", True, 'black', 'white')

    def event_handler(event):
        # eh
        nonlocal surf1, surf2
        if event.type == pygame.VIDEORESIZE:
            surf1 = pygame.Surface((app.screen.width, app.screen.height // 2))
            surf2 = pygame.Surface((app.screen.width, app.screen.height // 2))

    for delta in app.loop(event_handler):
        view1.lerp_to(app.player_pos.center, 0.1)
        view2.lerp_to(app.player_pos.center, 0.1)

        surf1.fill('black')
        bbox = view1.get_bounding_box(surf1.get_rect())
        view1.render(surf1, get_tiles_for_bbox(app.tiles, bbox))
        view1.render(surf1, [
            (app.player_pos.topleft, app.player_surf)
        ])

        surf2.fill('black')
        bbox = view2.get_bounding_box(surf2.get_rect())
        view2.render(surf2, get_tiles_for_bbox(app.tiles, bbox))
        view2.render(surf2, [
            (app.player_pos.topleft, app.player_surf)
        ])

        app.screen.blit(surf1, (0, 0))
        app.screen.blit(surf2, (0, app.screen.height // 2))

        app.screen.blit(text1, (10, 10))
        app.screen.blit(text2, (10, 10 + app.screen.height // 2))


if __name__ == '__main__':
    main()
