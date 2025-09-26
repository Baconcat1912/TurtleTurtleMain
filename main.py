import importlib
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
suvat = kinematics.suvat


class TurtleMotionController:
    """Advance a kinematics.suvat instance and keep a TurtleLib turtle in sync."""

    STEP_SIZE = 0.001  # seconds, matches the fixed timestep used inside suvat.move()

    def __init__(self, turtle_obj, motion_model, x_position):
        self.turtle_obj = turtle_obj
        self.motion_model = motion_model
        self.x_position = float(x_position)
        self._residual_time = 0.0

    def step(self, dt):
        model = self.motion_model

        if model.acceleration == 0 and model.ini_velo == 0 and model.height <= 0:
            self._residual_time = 0.0
            self._set_pose(model.height)
            return

        total_time = self._residual_time + dt
        steps = int(total_time // self.STEP_SIZE)
        if steps == 0:
            self._residual_time = total_time
            return

        self._residual_time = total_time - steps * self.STEP_SIZE

        start_height = model.height
        for _ in range(steps):
            model.move()
            model.time += self.STEP_SIZE
            if model.direction == "down" and model.height <= 0:
                model.height = 0.0
                model.ini_velo = 0.0
                model.final_velo = 0.0
                model.acceleration = 0.0
                self._residual_time = 0.0
                break

        new_height = max(0.0, model.height)
        elapsed = max(steps * self.STEP_SIZE, 1e-9)
        vertical_velocity = (new_height - start_height) / elapsed

        model.displacement = abs(new_height - start_height)

        # Vertical velocity comes from the kinematics model; horizontal velocity stays zero.
        moveturtle(self.turtle_obj, 0.0, vertical_velocity)
        self._set_pose(new_height)

    def _set_pose(self, height):
        self.turtle_obj.pos = (self.x_position, height)
        self.turtle_obj.draw_frame()


screen = turtle.Screen()
screen.setup(width=900, height=600)

fit_world_to_height(screen, y_min=0.0, y_max=80.0, margin_frac=0.15)
draw_ground(y=0)

alpha_motion = suvat(0, kinematics.g, 0, 0, 0, 80, "down")
beta_motion = suvat(20, -kinematics.g, 0, 0, 0, 0, "up")

a = drawturtle(0.02, -10, alpha_motion.height, 0)
b = drawturtle(0.02, 0, beta_motion.height, 0)

moveturtle(a, 0.0, 0.0)
moveturtle(b, 0.0, 0.0)

animateturtle(a, 1)
animateturtle(b, 1)

alpha_controller = TurtleMotionController(a, alpha_motion, -10)
beta_controller = TurtleMotionController(b, beta_motion, 0)


def on_frame(dt):
    alpha_controller.step(dt)
    beta_controller.step(dt)


add_frame_callback(on_frame)

turtle.done()
