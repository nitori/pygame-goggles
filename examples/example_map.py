import pygame

from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App((1000, 600))

    view = Visor(
        VisorMode.RegionLetterbox,
        initial_region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    map_view = Visor(
        VisorMode.RegionLetterbox,
        initial_region=(0, 0, 1000, 750),
        limits=app.limits,
    )
    map_surface = pygame.Surface((100, 75))

    view.move_to(app.player_pos.center)
    map_view.move_to(app.player_pos.center)

    for delta in app.loop(60):
        view.lerp_to(app.player_pos.center, 0.1)
        map_view.move_to(app.player_pos.center)

        bbox = view.get_bounding_box(app.screen.get_rect())
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))
        view.render(app.screen, [
            (app.player_pos.topleft, app.player_surf)
        ])

        bbox = map_view.get_bounding_box(map_surface.get_rect())
        map_surface.fill('black')
        map_view.render(map_surface, app.get_tiles_for_bbox(app.tiles, bbox))
        map_view.render(map_surface, [
            (app.player_pos.topleft, app.player_surf)
        ])

        area = view.get_region_screen_rect(app.screen.get_rect())
        map_surf_temp = view.scale_surf(app.screen.get_rect(), map_surface)
        app.screen.blit(map_surf_temp, (area.right - map_surf_temp.width, area.bottom - map_surf_temp.height))


if __name__ == '__main__':
    main()
