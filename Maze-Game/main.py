import turtle as t
import random

# Variables ---------

# Constants
WALLS = 33
PATH_WIDTH = 16
GAME_OVER = False  # Flag to track if the game is over
"""
ChatGPT implemented the wall hitting system
"""
wall_segments = []  # List to store wall segment coordinates

# Background setup
wn = t.Screen()
wn.tracer(False)
wn.setup(width=0.8, height=0.85, startx=None, starty=-50)

# Maze-drawing turtle
maze = t.Turtle()
maze.speed(1)
maze.hideturtle()
maze.pensize(4)
maze.color("darkorchid")

# Runner turtle
run = t.Turtle()
run.pensize(4)
run.color("red")
run.speed(5)

# Functions ---------

# Spiral function
def spiral():
    maze.lt(90)
    for i in range(2, WALLS + 1, 2):
        Wall(i)
        maze.lt(90)
        Wall(i)
        maze.lt(90)

# Door function
def Door(DOOR):
    length = PATH_WIDTH * DOOR
    x1, y1 = maze.pos()
    maze.fd(length)
    x2, y2 = maze.pos()
    wall_segments.append((x1, y1, x2, y2))  # Store door segment - ChatGPT
    maze.penup()
    maze.fd(2*PATH_WIDTH)
    maze.pendown()

# Barrier function
def Barrier(BARRIER, i):
    if (i % 3 != 0):
        length = PATH_WIDTH * BARRIER
        x1, y1 = maze.pos()
        maze.fd(length)
        x2, y2 = maze.pos()
        wall_segments.append((x1, y1, x2, y2))  # Store barrier segment - ChatGPT
        maze.lt(90)
        maze.fd(2*PATH_WIDTH)
        maze.bk(2*PATH_WIDTH)
        maze.rt(90)
    else:
        maze.fd(PATH_WIDTH * BARRIER)

# Wall function - includes the Door, the Barrier, and the Rest of the wall
def Wall(i):
    length = PATH_WIDTH * i
    if i > 6:
        i = i-2
        DOOR = 2*random.randint(1, (i-1)//2)
        BARRIER = 2*random.randint(1, (i-1)//2)
        while BARRIER == DOOR:
            BARRIER = 2*random.randint(1, (i-1)//2)
        REST = (i - max(DOOR, BARRIER))
        if DOOR < BARRIER:
            Door(DOOR)
            Barrier(BARRIER-DOOR, i)
            x1, y1 = maze.pos()
            maze.fd(REST * PATH_WIDTH)
            x2, y2 = maze.pos()
            wall_segments.append((x1, y1, x2, y2))
        else:
            Barrier(BARRIER, i)
            Door(DOOR-BARRIER)
            x1, y1 = maze.pos()
            maze.fd(REST * PATH_WIDTH)
            x2, y2 = maze.pos()
            wall_segments.append((x1, y1, x2, y2))
    elif i > 2:
        x1, y1 = maze.pos()
        maze.fd(length)
        x2, y2 = maze.pos()
        wall_segments.append((x1, y1, x2, y2))
    else:
        maze.pu()
        maze.fd(length)
        maze.pd()

# Check if runner collides with any wall segment
"""
ChatGPT made this!
"""
def check_wall_collision():
    global GAME_OVER
    x, y = run.pos()
    for x1, y1, x2, y2 in wall_segments:
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            GAME_OVER = True
            run.color("gray")
            print("Game Over! You hit a wall.")
            disable_inputs()
            return

# Disable all movement inputs
def disable_inputs():
    wn.onkeypress(None, "d")
    wn.onkeypress(None, "w")
    wn.onkeypress(None, "a")
    wn.onkeypress(None, "s")
    wn.onkeypress(None, "g")

# Movement Functions
def right():
    if not GAME_OVER:
        run.setheading(0)

def up():
    if not GAME_OVER:
        run.setheading(90)

def left():
    if not GAME_OVER:
        run.setheading(180)

def down():
    if not GAME_OVER:
        run.setheading(270)

def move():
    if not GAME_OVER:
        run.fd(PATH_WIDTH)
        check_wall_collision()

# Game Events ----------
spiral()
wn.tracer(True)
wn.onkeypress(right, "d")
wn.onkeypress(up, "w")
wn.onkeypress(left, "a")
wn.onkeypress(down, "s")
wn.onkeypress(move, "g")
wn.listen()
wn.exitonclick()