import pygame

from pygame_goggles import View, ViewMode
from common import App


def main():
    app = App()

    view = View(
        ViewMode.RegionLetterbox,
        initial_region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    view.move_to(app.player_pos.center)

    def event_handler(event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                view.region.scale_by_ip(2, 2)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                view.region.scale_by_ip(0.5, 0.5)

    for delta in app.loop(60, event_handler):
        view.move_to(app.player_pos.center)
        bbox = view.get_bounding_box(app.screen.get_rect())
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))
        view.render(app.screen, [
            (app.player_pos.topleft, app.player_surf)
        ])


if __name__ == '__main__':
    main()
