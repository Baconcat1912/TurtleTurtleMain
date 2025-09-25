# TurtleTurtleMain — TurtleLib

## Quick Start

```python
# quick_start.py
import turtle
import TurtleLib as tl

# Optional window setup
screen = turtle.Screen()
screen.setup(width=900, height=600)

# Fit world to a vertical range and draw a ground line at y=0
tl.fit_world_to_height(screen, y_min=0.0, y_max=80.0, margin_frac=0.15)
tl.draw_ground(y=0)

# Create two turtles
alice = tl.drawturtle(size=0.02, posx=-10, posy=80, orientation=0)
bob   = tl.drawturtle(size=0.02, posx=0,   posy=0,  orientation=0)

# Start limb animation (cycles per second)
tl.animateturtle(alice, animationspeed=1.0)
tl.animateturtle(bob,   animationspeed=1.0)

# Start the frame loop and show the window
tl.start_frame_loop()
```

Run with: `python quick_start.py`


## API Reference

- `drawturtle(size, posx, posy, orientation)`: Creates, registers, and draws a new turtle character. Returns the instance.
- `animateturtle(obj, animationspeed)`: Starts limb animation for `obj` at cycles per second.
- `stopturtle(obj)`: Stops limb animation for `obj`.
- `moveturtle(obj, vx_per_sec, vy_per_sec)`: Sets the constant velocity for `obj` in world units per second.
- `tpturtle(obj, x, y, orientation_deg=None)`: Instantly sets position (and optionally orientation) and redraws the frame.
- `add_frame_callback(func)` / `remove_frame_callback(func)`: Register a function receiving `dt` seconds each frame for custom logic.
- `start_frame_loop()`: Ensures the ticker is running and enters the GUI main loop (blocking).
- `sleep_nonblocking(ms, callback)`: Schedules `callback` to run after `ms` milliseconds without blocking frames.
- `fit_world_to_height(screen, y_min, y_max, x_center=0.0, margin_frac=0.1)`: Sets world coordinates so the vertical range is fully visible with margin and the horizontal range matches the window aspect ratio (no distortion).
- `draw_ground(y=0)`: Draws a horizontal line across the current world coordinates at height `y`.

## Tips

- Call `start_frame_loop()` once you’ve set up all turtles and callbacks.
- If you need to stop the program manually, close the window or interrupt the process.
- For consistent sizing, set world coordinates up front with `fit_world_to_height` before creating objects.
- Multiple turtles are supported; each instance is updated by the shared ticker, but has it's own class.

