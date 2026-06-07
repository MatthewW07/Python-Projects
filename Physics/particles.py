import pygame
import numpy as np
from itertools import combinations

pygame.init()


BLACK = (0, 0, 0)
BLUE = (40, 120, 240)
GRAY = (200, 200, 200)
RADIUS = 10
size = 700
center = np.array([size / 2, size / 2])
rate = 60
dt = 1 / rate
k = 9e9


screen = pygame.display.set_mode((size, size))

class Particle:
    def __init__(self, charge, mass, position, velocity):
        self.q = charge
        self.m = mass
        self.x = np.array(position, dtype=float)
        self.v = np.array(velocity, dtype=float)
        self.radius = RADIUS

def update_particles(particles):
    n = len(particles)
    forces = [np.zeros(2, dtype=float) for _ in range(n)]

    for i, j in combinations(range(n), 2):
        p1, p2 = particles[i], particles[j]

        r = p1.x - p2.x
        r2 = np.dot(r, r)
        r_mag = np.sqrt(r2)
        if r_mag <= p1.radius + p2.radius:
            p1.v, p2.v = p2.v, p1.v
            continue
        r_unit = r / r_mag
        F = k * p1.q * p2.q / r2 * r_unit
        forces[i] += F
        forces[j] -= F

    for i, p in enumerate(particles):
        a = forces[i] / p.m
        p.v += a * dt
        p.x += p.v * dt

        if p.x[0] - p.radius < 0:
            p.x[0] = p.radius
            p.v[0] *= -1
        if p.x[0] + p.radius > size:
            p.x[0] = size - p.radius
            p.v[0] *= -1
        if p.x[1] - p.radius < 0:
            p.x[1] = p.radius
            p.v[1] *= -1
        if p.x[1] + p.radius > size:
            p.x[1] = size - p.radius
            p.v[1] *= -1

def circle_arrange(n, radius, charge, velocity=0, alt=False):
    center = np.array([size // 2, size // 2])
    particles = []
    theta = (2 * np.pi) / n
    for i in range(n):
        q = charge * -1 if (i % 2 == 0 and alt) else charge
        pos = center + radius * np.array([np.cos(i * theta), np.sin(i * theta)])
        vel = velocity * np.array([-np.sin(i * theta), np.cos(i * theta)])
        particles.append(Particle(q, 1, pos, vel))
    return particles


particles = [
    Particle(-5e-4, 1, center + (100, 100), (1, 1)),    
    Particle(5e-4, 1, center + (-100, 100), (-1, 1)),
    Particle(-5e-4, 1, center + (100, -100), (1, -1)),
    Particle(5e-4, 1, center + (-100, -100), (-1, -1)),
]

# particles = circle_arrange(16, 200, 5e-4, velocity=0.5, alt=True) + circle_arrange(16, 300, -4e-4, velocity=0.5, alt=True)

running = True
while running:

    update_particles(particles)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    for particle in particles:
        pygame.draw.circle(screen, GRAY, particle.x, particle.radius)

    pygame.display.flip()


pygame.quit()

        