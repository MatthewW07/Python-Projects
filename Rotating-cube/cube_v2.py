
import math as m
import pygame as py


WIDTH        =  600       
HEIGHT       =  600       
BGCOLOR      =  'black'   
TEXTCOLOR    =  'white' 
THICK        =  3      
DISTANCE     =  600    
K1           =  600  
FPS          =  20      
SENSITIVITY  =  0.0008   
CUBESIZE     =  100      


running       = True   
mouseDownPos  = None   

A = 0.00 
B = 0.00 

shapes = {
  'triangle': {
    'vertices': [
      [+0, +1.1547, 0],
      [-1, -0.5774, 0],
      [+1, -0.5774, 0],
    ],
    'edges': [
      [0, 1], [1, 2], [2, 0]
    ],
    'color': 'red'
  },
  'square': {
    'vertices': [
      [+1, +1, 0],
      [-1, +1, 0],
      [-1, -1, 0],
      [+1, -1, 0],
    ],
    'edges': [
      [0, 1], [1, 2], 
      [2, 3], [3, 0]
    ],
    'color': 'blue'
  },
  'cube': {
    'vertices': [
      [+1, +1, +1],
      [-1, +1, +1],
      [+1, -1, +1],
      [+1, +1, -1],
      [-1, -1, +1],
      [+1, -1, -1],
      [-1, +1, -1],
      [-1, -1, -1],
    ],
    'edges': [
      [0, 1], [3, 6],
      [1, 4], [6, 7],
      [2, 4], [5, 7],
      [0, 2], [3, 5],
      [2, 5], [1, 6],
      [0, 3], [4, 7]
    ],
    'color': 'green'
  },
  'octahedron': {
    'vertices': [
      [+1.5, +0.0, +0.0],
      [+0.0, +1.5, +0.0],
      [-1.5, +0.0, +0.0],
      [+0.0, -1.5, +0.0],
      [+0.0, +0.0, +1.5],
      [+0.0, +0.0, -1.5]
    ],
    'edges': [
      [0, 1], [1, 2],
      [2, 3], [3, 0],
      [0, 4], [1, 4],
      [2, 4], [3, 4],
      [0, 5], [1, 5],
      [2, 5], [3, 5]
    ],
    'color': 'orange'
  }, 
}

curShapes = ['cube']


def rot(x, y, z):
  xAxis_x = x
  xAxis_y = y * m.cos(A) - z * m.sin(A)
  xAxis_z = y * m.sin(A) + z * m.cos(A)

  yAxis_x = xAxis_x * m.cos(B) + xAxis_z * m.sin(B)
  yAxis_y = xAxis_y
  yAxis_z = xAxis_z * m.cos(B) - xAxis_x * m.sin(B)

  return round(yAxis_x, 6), round(yAxis_y, 6), round(yAxis_z, 6)


def project(x, y, z):
  factor = K1 / (z + DISTANCE)
  projX = int(WIDTH / 2 - x * factor)
  projY = int(HEIGHT / 2 + y * factor)
  return projX, projY

def update(curShapes):
  screen.fill(BGCOLOR)
  drawButtons()

  global shapes
  for shape in shapes:
    if shape in curShapes:
      Points = []
      vertices = shapes[shape]['vertices']
      edges = shapes[shape]['edges']
      color = shapes[shape]['color']

      for v in range(len(vertices)):
        vertex = vertices[v] 
        x, y, z = rot(vertex[0], vertex[1], vertex[2]) 
        if (z + DISTANCE == 0):
          z += 0.1
        vertices[v] = [x,y,z]
        Points.append(project(x * CUBESIZE, y * CUBESIZE, z * CUBESIZE)) 

      for edge in edges:
        py.draw.line(screen, color, Points[edge[0]], Points[edge[1]], THICK)

  py.display.flip()
  clock.tick(FPS)


py.init()
py.display.set_caption("Rotating Cube")
screen = py.display.set_mode((WIDTH, HEIGHT))
clock = py.time.Clock()


buttons   = []
yPos      = HEIGHT - 100
btnWidth  = 120 
btnHeight = 50  
spacing   = (WIDTH - len(shapes) * btnWidth) // (len(shapes) + 1)


for idx, shape in enumerate(shapes.keys()):
  xPos = spacing + idx * (btnWidth + spacing)
  rect = py.Rect(xPos, yPos, btnWidth, btnHeight) 
  buttons.append((shape, rect)) 

def drawButtons():
  font = py.font.SysFont('Courier', 15)
  for shape, rect in buttons:
    color = shapes[shape]['color']
    py.draw.rect(screen, color, rect, 2) 
    text = font.render(shape, True, 'white') 
    textRect = text.get_rect(center=rect.center) 
    screen.blit(text, textRect)


while True:
  A *= 0.96
  B *= 0.96

  for event in py.event.get():
    if event.type == py.QUIT:
      py.quit()

    elif event.type == py.KEYDOWN:
      if event.key == py.K_SPACE:
        running = not running

    elif event.type == py.MOUSEBUTTONDOWN:
      if event.button == 1:
        buttonClicked = False 

        for shape, rect in buttons:
          if rect.collidepoint(event.pos):
            buttonClicked = True
            if shape in curShapes:
              curShapes.remove(shape)
            else:
              curShapes.append(shape)
            screen.fill(BGCOLOR) 
 
        if not buttonClicked:
          mouseDownPos = event.pos
        
    elif event.type == py.MOUSEBUTTONUP:
      if event.button == 1 and mouseDownPos is not None:
  
        x1, y1 = mouseDownPos
        x2, y2 = event.pos

        changeX = x2 - x1
        changeY = y2 - y1

        B += changeX * SENSITIVITY
        A += changeY * SENSITIVITY
    
        mouseDownPos = None

  if running:
    update(curShapes)