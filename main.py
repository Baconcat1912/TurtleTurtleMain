import importlib
import math
import tkinter as tk
import turtle

from TurtleLib import (
    add_frame_callback,
    animateturtle,
    draw_ground,
    drawturtle,
    fit_world_to_height,
    moveturtle,
)


# Use the shared kinematics module for all vertical motion calculations.
kinematics = importlib.import_module("kinematics")


class TurtleMotionController:
    """Keep a TurtleLib turtle synced to an analytic motion model."""

    def __init__(self, turtle_obj, x_position, state_func, initial_height, label_turtle=None, label_offset=(40.0, 0.0)):
        self.turtle_obj = turtle_obj
        self.x_position = float(x_position)
        self.state_func = state_func
        self.initial_height = float(initial_height)
        self.label_turtle = label_turtle
        self.label_offset = label_offset

        self.current_time = 0.0
        self.current_height = float(initial_height)
        self.current_velocity = 0.0
        self.total_displacement = 0.0

    def set_time(self, time_value):
        clamped_time = max(0.0, float(time_value))
        height, velocity = self.state_func(clamped_time)
        if height <= 0.0:
            height = 0.0
            velocity = 0.0

        self.current_time = clamped_time
        self.current_height = height
        self.current_velocity = velocity
        self.total_displacement = self.current_height - self.initial_height

        moveturtle(self.turtle_obj, 0.0, self.current_velocity)
        self._set_pose(self.current_height)

    def step(self, dt):
        self.set_time(self.current_time + dt)

    def update_label(self, relative_delta):
        if self.label_turtle is None:
            return
        self.label_turtle.clear()
        label_x = self.x_position + self.label_offset[0]
        label_y = self.current_height + self.label_offset[1]
        text = (
            f"v: {self.current_velocity:+.2f} m/s\n"
            f"ds: {self.total_displacement:+.2f} m\n"
            f"dy: {relative_delta:+.2f} m"
        )
        self.label_turtle.goto(label_x, label_y)
        self.label_turtle.write(text, align="left", font=("Arial", 12, "normal"))

    def get_height(self):
        return self.current_height

    def _set_pose(self, height):
        self.turtle_obj.pos = (self.x_position, height)
        self.turtle_obj.draw_frame()


G = float(kinematics.g)

ALPHA_INITIAL_HEIGHT = 80.0
ALPHA_INITIAL_VELOCITY = 0.0

BETA_INITIAL_HEIGHT = 0.0
BETA_INITIAL_VELOCITY = 20.0

ALPHA_STOP_TIME = math.sqrt((2.0 * ALPHA_INITIAL_HEIGHT) / G) if G > 0 else 0.0
BETA_STOP_TIME = (2.0 * BETA_INITIAL_VELOCITY) / G if G > 0 else 0.0
MAX_TIME = max(ALPHA_STOP_TIME, BETA_STOP_TIME)


def alpha_state(time_sec):
    t = max(0.0, float(time_sec))
    height = ALPHA_INITIAL_HEIGHT + ALPHA_INITIAL_VELOCITY * t - 0.5 * G * t * t
    velocity = ALPHA_INITIAL_VELOCITY - G * t
    if height <= 0.0:
        return 0.0, 0.0
    return height, velocity


def beta_state(time_sec):
    t = max(0.0, float(time_sec))
    height = BETA_INITIAL_HEIGHT + BETA_INITIAL_VELOCITY * t - 0.5 * G * t * t
    velocity = BETA_INITIAL_VELOCITY - G * t
    if height <= 0.0:
        return 0.0, 0.0
    return height, velocity


screen = turtle.Screen()
screen.setup(width=900, height=600)
try:
    # Keep the turtle window above other application windows.
    screen._root.attributes("-topmost", True)
except Exception:
    pass

fit_world_to_height(screen, y_min=0.0, y_max=80.0, margin_frac=0.15)
draw_ground(y=0)

a = drawturtle(0.02, -10, ALPHA_INITIAL_HEIGHT, 0)
b = drawturtle(0.02, 0, BETA_INITIAL_HEIGHT, 0)

moveturtle(a, 0.0, 0.0)
moveturtle(b, 0.0, 0.0)

animateturtle(a, 1)
animateturtle(b, 1)

alpha_label = turtle.Turtle()
alpha_label.hideturtle()
alpha_label.penup()
alpha_label.speed(0)
alpha_label.color("black")

beta_label = turtle.Turtle()
beta_label.hideturtle()
beta_label.penup()
beta_label.speed(0)
beta_label.color("black")

alpha_controller = TurtleMotionController(
    a,
    -10,
    alpha_state,
    ALPHA_INITIAL_HEIGHT,
    label_turtle=alpha_label,
    label_offset=(-120.0, 0.0),
)
beta_controller = TurtleMotionController(
    b,
    0,
    beta_state,
    BETA_INITIAL_HEIGHT,
    label_turtle=beta_label,
    label_offset=(40.0, 0.0),
)


playback_rate = 1.0
simulation_time = 0.0
paused = False
pause_button = None
time_scrubber = None
updating_scrubber = False


def clamp_time(value):
    return max(0.0, min(MAX_TIME, float(value)))


def set_playback_rate(value):
    global playback_rate
    try:
        playback_rate = float(value)
    except (TypeError, ValueError):
        playback_rate = 1.0


def toggle_pause():
    global paused
    paused = not paused
    if pause_button is not None:
        pause_button.config(text="Resume" if paused else "Pause")


def on_scrub(value):
    global simulation_time
    if updating_scrubber:
        return
    try:
        simulation_time = clamp_time(value)
    except (TypeError, ValueError):
        return
    update_simulation(simulation_time)


def setup_controls(screen_obj):
    global pause_button, time_scrubber
    root = getattr(screen_obj, "_root", None)
    if root is None:
        return

    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.RIGHT, anchor="ne", padx=12, pady=12)

    rate_slider = tk.Scale(
        control_frame,
        from_=-3.0,
        to=3.0,
        resolution=0.1,
        orient=tk.HORIZONTAL,
        length=200,
        label="Playback Rate",
        command=set_playback_rate,
    )
    rate_slider.set(playback_rate)
    rate_slider.pack(fill=tk.X)

    time_scrubber = tk.Scale(
        control_frame,
        from_=0.0,
        to=MAX_TIME,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        length=200,
        label="Scrub Time",
        command=on_scrub,
    )
    time_scrubber.set(simulation_time)
    time_scrubber.pack(fill=tk.X, pady=(8, 0))

    pause_button = tk.Button(control_frame, text="Pause", command=toggle_pause)
    pause_button.pack(fill=tk.X, pady=(8, 0))


def update_simulation(time_value):
    global simulation_time
    clamped = clamp_time(time_value)
    simulation_time = clamped
    alpha_controller.set_time(clamped)
    beta_controller.set_time(clamped)

    relative = alpha_controller.get_height() - beta_controller.get_height()
    alpha_controller.update_label(relative)
    beta_controller.update_label(-relative)


setup_controls(screen)
update_simulation(simulation_time)


def on_frame(dt):
    global simulation_time, updating_scrubber

    if not paused and playback_rate != 0.0:
        new_time = clamp_time(simulation_time + playback_rate * dt)
        if new_time != simulation_time:
            simulation_time = new_time
            if time_scrubber is not None:
                updating_scrubber = True
                time_scrubber.set(simulation_time)
                updating_scrubber = False

    update_simulation(simulation_time)


add_frame_callback(on_frame)

turtle.done()
