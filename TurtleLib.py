import turtle
import math
from functools import partial
# --------- Setup ---------
screen = turtle.Screen()
screen.tracer(0)  # Draws instantly
screen.colormode(1.0)

# Registry + single 30fps ticker that services any animating instances
_INSTANCES = []
_FRAME_CALLBACKS = []
_TICK_RUNNING = False
_FRAME_MS = 33           # ~30 FPS
_DT = _FRAME_MS / 1000.0

# --------- Character Class ---------
class TurtleCharacter:
    # Base geometry
    SHELL_R    = 100
    HEAD_R     = 50
    LIMB_R     = 40
    HEX_SIDE   = 30
    HEX_RING_R = 60
    TAIL_SIDE  = 30

    CENTER   = (0, 0)
    HEAD_C   = (0, 135)
    ARM_L_C  = (-120, 60)
    ARM_R_C  = (120, 60)
    LEG_L_C  = (-70, -100)
    LEG_R_C  = (70, -100)
    TAIL_C   = (16, -99)
    HEX_CENTER_C = (-4, -7)

    # Eyes
    EYE_L = (-20, 155)
    EYE_R = ( 20, 155)
    PUPIL_L = (-20, 156)
    PUPIL_R = ( 20, 156)

    def __init__(self, size, posx, posy, orientation_deg):
        self.size = float(size)
        self.pos  = (float(posx), float(posy))
        self.ori  = float(orientation_deg)

        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()

        # Precompute hex ring centers (local)
        self.hex_ring_cs = []
        for ang in range(0, 360, 60):
            x = self.HEX_RING_R * math.cos(math.radians(ang))
            y = self.HEX_RING_R * math.sin(math.radians(ang))
            self.hex_ring_cs.append((x + self.HEX_CENTER_C[0], y + self.HEX_CENTER_C[1]))

        # Animation state
        self.phase = 0.0       # radians
        self.speed = 0.0       # cycles/sec for legs
        self._animate = False  # whether this instance is animating
        self.velocity = (0.0, 0.0)  # units per second in screen space

    # ---- transforms (local -> world) ----
    def _to_world(self, px, py):
        sx, sy = px * self.size, py * self.size
        r = math.radians(self.ori)
        rx = sx * math.cos(r) - sy * math.sin(r)
        ry = sx * math.sin(r) + sy * math.cos(r)
        return self.pos[0] + rx, self.pos[1] + ry

    def _goto_local(self, x, y):
        wx, wy = self._to_world(x, y)
        self.t.penup()
        self.t.goto(wx, wy)

    def _setheading_local(self, deg):
        self.t.setheading(deg + self.ori)

    def _forward_local(self, d):
        self.t.forward(d * self.size)

    def _left_local(self, deg):
        self.t.left(deg)

    def _circle_local(self, radius):
        self.t.circle(radius * self.size)

    # ---- primitives ----
    def _draw_circle(self, color, radius, x, y):
        self._goto_local(x, y - radius)
        self._setheading_local(0)
        self.t.pendown()
        self.t.fillcolor(color)
        self.t.begin_fill()
        self._circle_local(radius)
        self.t.end_fill()
        self.t.penup()

    def _draw_tail(self, color, x, y, heading_deg_local=180):
        self._goto_local(x, y)
        self._setheading_local(heading_deg_local)
        self.t.pendown()
        self.t.fillcolor(color)
        self.t.begin_fill()
        for _ in range(3):
            self._forward_local(self.TAIL_SIDE)
            self._left_local(120)
        self.t.end_fill()
        self.t.penup()

    def _draw_hex(self, color, size, x, y):
        self._goto_local(x, y)
        self._setheading_local(0)
        self._forward_local(size)
        self._left_local(90)
        self.t.pendown()
        self.t.fillcolor(color)
        self.t.begin_fill()
        for _ in range(6):
            self._forward_local(size)
            self._left_local(60)
        self.t.end_fill()
        self.t.penup()

    # ---- one frame (with animated legs + arms + tail wag) ----
    def draw_frame(self):
        self.t.clear()

        # Body (static parts)
        self._draw_circle("green",     self.SHELL_R, *self.CENTER)
        self._draw_circle("darkgreen", self.HEAD_R,  *self.HEAD_C)

        # --- Synchronized limb motion (front & back), mirrored left/right ---
        # Back legs: base ellipse
        Ax_leg, Ay_leg = 12, 20
        phase_leg = -self.phase

        dx_leg = Ax_leg * math.sin(phase_leg)
        dy_leg = Ay_leg * math.cos(phase_leg)

        # Legs (back)
        Lx0, Ly0 = self.LEG_L_C
        Rx0, Ry0 = self.LEG_R_C
        self._draw_circle("darkgreen", self.LIMB_R, Lx0 + dx_leg, Ly0 + dy_leg)  # left back
        self._draw_circle("darkgreen", self.LIMB_R, Rx0 - dx_leg, Ry0 + dy_leg)  # right back (mirror X)

        # Front legs (arms): half a phase out of sync, smaller amplitude
        ARM_SCALE = 0.6
        Ax_arm, Ay_arm = Ax_leg * ARM_SCALE, Ay_leg * ARM_SCALE
        phase_arm = phase_leg + math.pi

        dx_arm = Ax_arm * math.sin(phase_arm)
        dy_arm = Ay_arm * math.cos(phase_arm)

        # Arms
        Lax, Lay = self.ARM_L_C
        Rax, Ray = self.ARM_R_C
        self._draw_circle("darkgreen", self.LIMB_R, Lax + dx_arm, Lay + dy_arm)  # left front
        self._draw_circle("darkgreen", self.LIMB_R, Rax - dx_arm, Ray + dy_arm)  # right front (mirror X)

        # Tail wag between 170° and 190°
        tail_angle = 180 + 10 * math.sin(self.phase)
        self._draw_tail("darkgreen", *self.TAIL_C, heading_deg_local=tail_angle)

        # Shell pattern
        self._draw_hex("darkgreen", self.HEX_SIDE, *self.HEX_CENTER_C)
        for c in self.hex_ring_cs:
            self._draw_hex("darkgreen", self.HEX_SIDE, *c)

        # Eyes
        self._draw_circle("white", 15, *self.EYE_L)
        self._draw_circle("white", 15, *self.EYE_R)
        self._draw_circle("black",  7, *self.PUPIL_L)
        self._draw_circle("black",  7, *self.PUPIL_R)

        self.t.goto(10000, 10000)

    def advance_phase(self, dt):
        self.phase += 2 * math.pi * self.speed * dt

    def set_velocity(self, vx, vy):
        self.velocity = (float(vx), float(vy))

    def _apply_motion(self, dt):
        if self.velocity == (0.0, 0.0):
            return
        px, py = self.pos
        vx, vy = self.velocity
        self.pos = (px + vx * dt, py + vy * dt)

    def _frame_step(self, dt):
        if self._animate:
            self.advance_phase(dt)
        self._apply_motion(dt)
        self.draw_frame()

    def start_animation(self, speed_cps):
        self.speed = float(speed_cps)
        self._animate = True
        _ensure_ticker()

    def stop_animation(self):
        self._animate = False


# --------- Public API ---------
def drawturtle(size, posx, posy, orientation):
    obj = TurtleCharacter(size, posx, posy, orientation)
    _register_instance(obj)
    obj.draw_frame()
    return obj

def animateturtle(obj, animationspeed):
    obj.start_animation(animationspeed)

def stopturtle(obj):
    obj.stop_animation()

def moveturtle(obj, vx_per_sec, vy_per_sec):
    obj.set_velocity(vx_per_sec, vy_per_sec)

def tpturtle(obj, x, y, orientation_deg=None):
    obj.pos = (float(x), float(y))
    if orientation_deg is not None:
        obj.ori = float(orientation_deg)
    obj.draw_frame()


def add_frame_callback(func):
    if func not in _FRAME_CALLBACKS:
        _FRAME_CALLBACKS.append(func)

def remove_frame_callback(func):
    if func in _FRAME_CALLBACKS:
        _FRAME_CALLBACKS.remove(func)

def start_frame_loop():
    _ensure_ticker()
    screen.mainloop()

def _register_instance(obj):
    if obj not in _INSTANCES:
        _INSTANCES.append(obj)
    _ensure_ticker()

def _ensure_ticker():
    global _TICK_RUNNING
    if _TICK_RUNNING:
        return
    _TICK_RUNNING = True

    def _tick():
        for inst in list(_INSTANCES):
            if hasattr(inst, "_frame_step"):
                inst._frame_step(_DT)
        for cb in list(_FRAME_CALLBACKS):
            cb(_DT)
        screen.update()
        screen.ontimer(_tick, _FRAME_MS)

    _tick()

def sleep_nonblocking(ms, callback):
    """
    Non-blocking sleep.
    - ms: delay in milliseconds
    - callback: function to call after the delay
    """
    turtle.ontimer(callback, ms)

def fit_world_to_height(screen, y_min, y_max, x_center=0.0, margin_frac=0.1):
    """
    Sets world coords so:
      - the full vertical range [y_min, y_max] is visible (with margin)
      - the horizontal range is chosen to match the window aspect ratio
      - no stretching/squishing occurs
    """
    screen.update()  # ensure correct window size
    win_w = screen.window_width()
    win_h = screen.window_height()
    aspect = win_w / win_h if win_h else 1.3333

    # add vertical margin
    y_range = (y_max - y_min)
    y_range *= (1 + 2 * margin_frac)
    y_mid = 0.5 * (y_min + y_max)
    y_lo  = y_mid - 0.5 * y_range
    y_hi  = y_mid + 0.5 * y_range

    # choose x range to match aspect (so no distortion)
    x_range = y_range * aspect
    x_lo = x_center - 0.5 * x_range
    x_hi = x_center + 0.5 * x_range

    screen.setworldcoordinates(x_lo, y_lo, x_hi, y_hi)

def draw_ground(y=0):
    """Draw a horizontal ground line at y using current world coordinates."""
    screen = turtle.Screen()
    # Read the world bounds from the underlying Tk canvas (public API).
    canvas = screen.getcanvas()
    x_min, y_min, x_max, y_max = map(float, canvas.cget('scrollregion').split())

    ground = turtle.Turtle()
    ground.hideturtle()
    ground.speed(0)
    ground.penup()
    ground.goto(x_min, y)
    ground.pendown()
    ground.goto(x_max, y)

# Animation stuff
SCALE = 1  # pixels per meter
DT = 0.02  # simulation timestep (s) ~50 FPS
H = 80 #Maximum height of simulation (in this case over 80m)


