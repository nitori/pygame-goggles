# Pygame Googles

Camera/Viewport library for pygame/pygame-ce

### 🧭 Camera/Viewport System – Feature Overview

- [x] Translate between world and screen coordinates (`world_to_screen`, `screen_to_world`)
    - Needed for input mapping (e.g. `screen_to_world(mouse_pos)`)
- [x] Support multiple view modes:
    - [x] Fixed world area (scales with screen), with or without padding
    - [ ] ~~Fixed zoom level (screen res affects visible area)~~
- [x] Camera movement via external control (`move_center_to(pos)`)
- [x] Optional clamping to world bounds / limits (camera can't move past edges)
- [x] Multiple views supported via independent instances (multi-camera/minimap/splitscreen)
- [x] Support lerping/smooth movement to a target position (or perhaps have the user do it themselves?)
    - [ ] Can probably get some more love, but a basic lerp already works.
- [x] Expose `get_current_bounding_box(surface_rect)` for rendering logic
    - Camera "requests" world region using the bounding box method above; game provides matching surfaces
    - [x] Accept surface size/rect for bounding box calculations (for the different view modes above)
- [ ] Handle zooming, including fractional zoom
    - [ ] UX: Optional **zoom-to-cursor** behavior (maintains world point under cursor)

### Optional stuff for now

- [ ] debug helpers (draw bounding box, show mouse world pos, etc.)
- [ ] Overscan/margin support for effects, camera shake, etc.

## View Modes

#### 1. Fixed Region (No Overscan)

- A specific world size (e.g. 400x300 units) is always shown.
- If the screen's aspect ratio differs, black bars (letterboxing) fill the space.
- Scaling happens to fit the screen, preserving aspect ratio.

#### 2. Fixed Region (With Overscan)

- A specific world size (e.g. 400x300) is the *minimum* shown.
- If the screen is larger/wider, *more* of the world is revealed (i.e. expands the visible region).
- No letterboxing; fills the screen with as much world as possible.

## Basic Usage

```python
# get a surface the view can draw on. Could also be screen directly.
surf = pygame.Surface(400, 300)

# Create a View instance
view = View(
    ViewMode.RegionLetterbox,  # One of two modes (see above)
    initial_region=(0, 0, 400, 300),  # world region to "view"
    limits=[-2000, -2000, 2000, 2000],  # Optional min/max x,y coords to constrain the view to.
)

while True:
    # ...

    # Get the world bounding box (it's a pygame.FRect, indicating the area of
    # the world that is currently visible)
    bbox = view.get_bounding_box(surf.get_rect())

    # Get iterable of surfaces, that cover the bounding box
    # This you need to implement yourself!
    # Return an iterable of tuples: (world_x, world_y, tile_surface)
    # Where tile_surface (at the moment) must have world coords width/height. Surfaces are expected to be
    # pre-rendered at world-scale (1 unit = 1 pixel in world space). The View system will scale them
    # appropriately based on screen resolution and view mode.
    tiles = world.get_tiles_iterable(bbox)

    # render tiles to surface, the view will autoscale them to the correct size.
    view.render(surf, tiles)

    # optional (if you don't use the screen directly), blit to screen:
    screen.blit(surf, (0, 0))

    # ...
```

If you have a player, that needs to be rendered on top of the map. Assuming `player.surf` holds
your players surface, and `player.rect` holds the players position:

```python
while True:
    # ...

    # update view based on player position *before* getting the bbox
    view.move_to(player.rect.center)  # view.lerp_to(...) is also possible
    bbox = view.get_bounding_box(surf.get_rect())

    # ... get tiles etc.

    # render map
    view.render(surf, tiles)

    # render the player using view.render, so it will be scaled correctly
    view.render(surf, [
        (player.rect.topleft, player.surf)
    ])

    # ...
```

### 📌 Example: Map + Minimap

See [`example_map.py`](examples/example_map.py) for a full working example of a main view and a minimap using two independent cameras.

![example_map.png](examples/screenshots/example_map.png)

---

See [`example_modes.py`](examples/example_modes.py) to demonstrate the difference between `ViewMode.RegionLetterbox` and `ViewMode.RegionExpand`.

![example_modes.png](examples/screenshots/example_modes.png)

---

See [`example_zoom.py`](examples/example_zoom.py) to demonstrate a simple way to zoom your view in and out.

![example_zoom.png](examples/screenshots/example_zoom.png)

---

See [`example_mouse.py`](examples/example_mouse.py) for a demonstration of tracking mouse screen pos to world tile position.

![example_mouse.png](examples/screenshots/example_mouse.png)

---

See [`example_ui.py`](examples/example_ui.py) for a simple UI example, of how to position them in the "active" area, in any ViewMode.

![example_ui.png](examples/screenshots/example_ui.png)
