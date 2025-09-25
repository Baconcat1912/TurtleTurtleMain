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