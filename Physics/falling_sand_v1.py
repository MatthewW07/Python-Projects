import numpy as np
import pygame

TILESIZE = 3

class FallingSand:
    def __init__(self, w=200, h=200, tileSize=TILESIZE):
        self.w = w
        self.h = h
        self.grid = np.zeros((h, w))
        self.tileSize = tileSize
        self.drawing = True
        self.running = False
        self.decay = 0.1
        self.drawRadius = 0

    def draw(self, x, y):
        gridX = x // self.tileSize
        gridY = y // self.tileSize
        if (gridX < 0 + self.drawRadius) or (gridX >= self.w - self.drawRadius):
            return
        if (gridY < 0 + self.drawRadius) or (gridY >= self.h - self.drawRadius):
            return
        
        if self.drawing:
            self.grid[max(0, gridY-self.drawRadius):min(self.h, gridY+self.drawRadius+1), max(0, gridX-self.drawRadius):min(self.w, gridX+self.drawRadius+1)] = np.random.uniform(0.95, 1.0, (2*self.drawRadius+1, 2*self.drawRadius+1))
        else:
            self.grid[max(0, gridY-self.drawRadius):min(self.h, gridY+self.drawRadius+1), max(0, gridX-self.drawRadius):min(self.w, gridX+self.drawRadius+1)] = 0.0

    def update(self):
        res = np.maximum(0.0, self.grid - self.decay)
        res[-1] = self.grid[-1]
        for i in range(self.h-2, -1, -1):
            for j in range(self.w):

                # Needs to move
                if self.grid[i][j] >= 0.95:

                    # Below is full
                    if self.grid[i+1][j] >= 0.95: 
                        p = np.random.uniform(0, 1)
                        r = 0.02
                        if (j > 0) and (p < r) and (self.grid[i+1][j-1] < 0.95):
                            res[i+1][j-1] = self.grid[i][j]
                        elif (j < self.w-1) and (p > 1-r) and (self.grid[i+1][j+1] < 0.95):
                            res[i+1][j+1] = self.grid[i][j]
                        else:
                            res[i][j] = self.grid[i][j]

                    # Moves down
                    else:
                        res[i+1][j] = self.grid[i][j]

        self.grid = res


    def addRandom():
        pass

    def valToColor(self, intensity):
        return 100 * (intensity * intensity) - 95

    def gridToColor(self):
        colorGrid = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        sand = (self.grid >= 0.95)
        sandValues = self.grid[sand]
        if np.any(sand):
            indices = np.where(sand)[0], np.where(sand)[1]
            intensity = self.valToColor(sandValues)
            colorGrid[indices[0], indices[1], 0] = 240 + 3*intensity
            colorGrid[indices[0], indices[1], 1] = 175 + 4*intensity
            colorGrid[indices[0], indices[1], 2] = 130 + 4*intensity

        partials = ((self.grid > 0.0) & (self.grid < 0.95))
        partialValues = self.grid[partials]

        lowPartials = (partialValues <= 0.7)
        highPartials = (partialValues > 0.7)

        if np.any(lowPartials):
            lowIndices = np.where(partials)[0][lowPartials], np.where(partials)[1][lowPartials]
            intensity = partialValues[lowPartials]
            colorGrid[lowIndices[0], lowIndices[1], 0] = (255 * intensity).astype(np.uint8)
            colorGrid[lowIndices[0], lowIndices[1], 1] = 0
            colorGrid[lowIndices[0], lowIndices[1], 2] = 0

        if np.any(highPartials):
            highIndices = np.where(partials)[0][highPartials], np.where(partials)[1][highPartials]
            intensity = partialValues[highPartials]
            colorGrid[highIndices[0], highIndices[1], 0] = 255
            colorGrid[highIndices[0], highIndices[1], 1] = (150 * intensity).astype(np.uint8)
            colorGrid[highIndices[0], highIndices[1], 2] = 0

        return colorGrid


if __name__=='__main__':

    pygame.init()
    sim = FallingSand()
    display = pygame.display.set_mode((sim.w * sim.tileSize, sim.h * sim.tileSize))
    pygame.display.set_caption("Falling Sand")
    framerate = 30
    clock = pygame.time.Clock()

    gridSurface = pygame.Surface((sim.w, sim.h))
    scaledSurface = pygame.Surface((sim.w * sim.tileSize, sim.h * sim.tileSize))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.running = not sim.running
                elif event.unicode.isdigit():
                    sim.drawRadius = int(event.unicode)
                    print(sim.drawRadius)

        clicks = pygame.mouse.get_pressed()
        if clicks[0]:
            x, y = pygame.mouse.get_pos()
            sim.draw(x, y)

        if sim.running:
            sim.update()

        colorGrid = sim.gridToColor()
        colorTranspose = np.transpose(colorGrid, (1, 0, 2))

        pygame.surfarray.blit_array(gridSurface, colorTranspose)
        pygame.transform.scale(gridSurface, (sim.w * sim.tileSize, sim.h * sim.tileSize), scaledSurface)
        display.blit(scaledSurface, (0, 0))

        pygame.display.flip()
        clock.tick(framerate)



    pygame.quit()
    quit()
