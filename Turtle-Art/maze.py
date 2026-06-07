import turtle as t
import random

# Constant variables:
WIDTH = 600
HEIGHT = 600
PADDING = 7
ROWS = 30
COLS = 30

CELLSIZE= (WIDTH-10) // COLS
DFSstack = []

# Screen set-up
bg = t.Screen()
bg.bgcolor("black")
bg.setup(WIDTH, HEIGHT)
bg.title("Random Maze Generator")
bg.tracer(False)

# Maze pen
maze = t.Turtle()
maze.pensize(CELLSIZE - 5)
maze.speed(0)
maze.color("lightgray")
maze.hideturtle()

# Start / End pen
style = t.Turtle()
style.pensize(CELLSIZE-6)
style.color("red")
style.shape("circle")
style.pu()

# Runner pen
run = t.Turtle()
run.pensize(4)
run.color("blue")
run.speed(0)

# Grid to track unvisited cells
grid = [[False] * COLS for _ in range(ROWS)]

# Shift coord. axis to Top Left Corner and Scale Grid
def coordinates(x, y):
    gridX = (x * CELLSIZE) - (WIDTH / 2) + (CELLSIZE / 2) + (PADDING)
    gridY = - (y * CELLSIZE) + (HEIGHT / 2) - (CELLSIZE / 2) - (PADDING)
    maze.goto(gridX, gridY)
    style.goto(gridX, gridY)

# Neighboring cells given current position
def getNeighbors(row, col):
    neighbors = []
    if row > 0 and not grid[row - 1][col]:
        neighbors.append((row-1, col))
    if row < ROWS - 1 and not grid[row + 1][col]:
        neighbors.append((row+1, col))
    if col > 0 and not grid[row][col - 1]:
        neighbors.append((row, col-1))
    if col < COLS - 1 and not grid[row][col + 1]:
        neighbors.append((row, col+1)) 
    if len(neighbors) > 0:
        return random.choice(neighbors)
    else:
        return False
    
# Maze generation:
# 1: Mark current cell as visited AND get a list of unvisited neighboring cells
# 2: If neighbor available: append coordinate to DFS stack
# 3: If no neighbor available: pop a cell from DFS stack and repeat
# 4: If no neighbor available AND stack empty: maze is complete
def mazeGenerator(start=(0,0)):
    cur = start
    maze.pu()
    coordinates(cur[0], cur[1])
    maze.pd()
    while True:
        grid[cur[0]][cur[1]] = True
        next = getNeighbors(cur[0], cur[1])
        if next:
            DFSstack.append(cur)
            cur = next
            coordinates(cur[0], cur[1])
        elif len(DFSstack) > 0:
            cur = DFSstack.pop()
            coordinates(cur[0], cur[1])
        else:
            style.stamp()
            return
        
# Movement Functions
# Movement Functions
def right():
    run.setheading(0)
def up():
    run.setheading(90)
def left():
    run.setheading(180)
def down():
    run.setheading(270)
def move():
    run.fd(CELLSIZE)

# Main Loop

mazeGenerator()
style.goto((ROWS-1) * CELLSIZE * 0.5, - (COLS-1) * CELLSIZE * 0.5)
style.stamp()
bg.tracer(True)

run.pu()
run.goto(-(ROWS-1) * CELLSIZE * 0.5 - (0.5 * CELLSIZE), (COLS-1) * CELLSIZE * 0.5 + (0.5 * CELLSIZE))
run.pd()
bg.onkeypress(right, "d")
bg.onkeypress(up, "w")
bg.onkeypress(left, "a")
bg.onkeypress(down, "s")
bg.onkeypress(move, "g")
bg.listen()
bg.exitonclick()