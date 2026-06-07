import pygame
import numpy as np

RED = (222, 0, 0)
BLUE = (0, 0, 222)
timeStep = 0.5
G = 9.8

class CelestialObject:
    def __init__(self, mass, radius, initialVelocity, position, color):
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(initialVelocity, dtype=np.float32)
        self.color = color

    def updateVelocity(self, allBodies, timeStep):
        for body in allBodies:
            if body != self:
                direction = body.position - self.position
                r = np.linalg.norm(direction)
                forceMagnitude = G * self.mass * body.mass / (r * r)
                acceleration = (forceMagnitude / self.mass) * (direction / r)
                self.velocity += acceleration

    def updatePosition(self, timeStep):
        self.position += self.velocity * timeStep


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    planet = CelestialObject(100, 10, [1, 1], [100, 300], RED)
    moon = CelestialObject(10, 5, [-0.5, -1], [150, 300], BLUE)
    bodies = [planet, moon]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for body in bodies:
            body.updateVelocity(bodies, timeStep)
        
        for body in bodies:
            body.updatePosition(timeStep)

        display.fill((0, 0, 0))

        for body in bodies:
            x, y = int(body.position[0]), int(body.position[1])
            pygame.draw.circle(display, body.color, (x, y), body.radius)

        pygame.display.flip()
        clock.tick(60)




    