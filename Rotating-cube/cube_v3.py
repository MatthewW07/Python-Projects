# Rotating cube with Turtle
import turtle as t
import math as m
import time

# Variables / Constants
A = 0.05
K1 = 10
DISTANCE = 10
FRAMES = 0.05

l = m.sqrt(2) / 2
shapes = {
    "cube" : [
    [l, l, l], [l, -l, l],
    [-l, l, l], [-l, -l, l],
    [l, l, -l], [l, -l, -l],
    [-l, l, -l], [-l, -l, -l],
    [1, 0, 1], [0, 1, 1],
    [-1, 0, 1], [0, -1, 1],
    [1, 0, -1], [0, 1, -1],
    [-1, 0, -1], [0, -1, -1],
    [1, 0, 0], [0, 1, 0], 
    [-1, 0, 0], [0, -1, 0],
    [0, 0, 1], [0, 0, -1,]
],
    "square" : [
    [1,1,0], [-1,1,0],
    [-1,-1,0], [1,-1,0],
]
}

vertices = shapes[input("Choose a shape: 'cube' or 'square': ")]
print(vertices)

wn = t.Screen()
wn.tracer(False)

pens =[]

for i in vertices:
    Vpen = t.Turtle()
    pens.append(Vpen)

# Turtle setup
for pen in pens:
    pen.shape("circle")
    pen.speed(0)
    pen.pensize("1")
    pen.pu()

# Rotations
def yRot(point, V):
    x, y, z = point[0], point[1], point[2]
    Rx = x * (m.cos(A)) + z * (m.sin(A))
    Ry = y
    Rz = x * (-m.sin(A)) + z * (m.cos(A))
    vertices[V] = [Rx, Ry, Rz]
    return [Rx, Ry, Rz]

def zRot(point, V):
    x, y, z = point[0], point[1], point[2]
    Rx = x * (m.cos(A)) + y * (-m.sin(A))
    Ry = x * (m.sin(A)) + y * (m.cos(A))
    Rz = z
    vertices[V] = [Rx, Ry, Rz]
    return [Rx, Ry, Rz]

# Projection function
def proj(point):
    x, y, z = point[0], point[1], point[2]
    factor = K1 / (z + DISTANCE)
    projX = int(x * factor) * 100
    projY = int(y * factor) * 100
    #return projX, projY
    return x*100, y*100

# Main Loop
while True:
    time.sleep(FRAMES)
    for V in range(len(pens)):
        point = vertices[V]
        pens[V].goto(proj(point))
        newPoint = zRot(yRot(point, V), V)
        pens[V].goto(proj(newPoint))
    wn.update() 

wn.exitonclick()

