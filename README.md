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

