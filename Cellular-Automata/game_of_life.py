import numpy as np
import pygame

# Current user inputs:
# 'SPACE'      = toggle Pause
# 'e'          = toggle Create or Destroy
# 'r'          = add Random Life
# 'LEFT_CLICK' = add or remove Life

class GameBoard:
    def __init__(self, size=(800, 800)):
        self.size = size

    def start_window(self):
        pygame.init()
        pygame.display.set_caption("Game of Life")
        display = pygame.display.set_mode(self.size)

        self.size = pygame.Surface(self.size)
        self.display = display

class GameOfLife:
    def __init__(self, w=800, h=800, TILESIZE=5, FPS=60):
        self.w = w
        self.h = h
        self.TILESIZE = TILESIZE
        self.FPS = FPS
        self.gameboard = GameBoard(size=(self.w, self.h))
        self.display_w = self.w * self.TILESIZE
        self.display_h = self.h * self.TILESIZE
        self.grid = np.zeros((self.h, self.w), dtype=np.float32)
        self.active = False
        self.trail = True
        self.adding_life = True
        self.nearby = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]

    def add_life(self, x, y):
        # (x, y) represents the MOUSE position
        if (x < 0) or (x > self.display_w):
            return
        if (y < 0) or (y > self.display_h):
            return
        x //= self.TILESIZE
        y //= self.TILESIZE
        if self.adding_life:
            self.grid[y][x] = 1.0
        else:
            self.grid[y][x] = 0.0


    def check_nearby_life(self):
        alive_mask = (self.grid == 1.0).astype(np.int8)
        sums = (
            np.roll(alive_mask, 1, axis=0) + np.roll(alive_mask, -1, axis=0) + 
            np.roll(alive_mask, 1, axis=1) + np.roll(alive_mask, -1, axis=1) + 
            np.roll(np.roll(alive_mask, 1, axis=0), 1, axis=1) +
            np.roll(np.roll(alive_mask, 1, axis=0), -1, axis=1) + 
            np.roll(np.roll(alive_mask, -1, axis=0), 1, axis=1) + 
            np.roll(np.roll(alive_mask, -1, axis=0), -1, axis=1)
        )
        return sums

    def update(self):
        # Updates self.grid
        sums = self.check_nearby_life()
        born = (sums == 3)
        survive = ((self.grid == 1.0) & (sums == 2))

        decay = 0.1
        new_grid = np.empty_like(self.grid)
        new_grid[born | survive] = 1.0
        new_grid[~(born | survive)] = np.maximum(0.0, self.grid[~(born | survive)] - decay)
        self.grid = new_grid

    def add_random_life(self):
        new_life = 100
        rows = np.random.randint(0, self.w, new_life)
        cols = np.random.randint(0, self.h, new_life)
        self.grid[rows, cols] = 1.0

    def grid_to_color(self):
        color = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        alive = (self.grid == 1.0)
        color[alive] = [255, 255, 180]

        if self.trail:
            dying = ((self.grid > 0.0) & (self.grid < 1.0))
            if np.any(dying):
                rows, cols = np.where(dying)
                vals = self.grid[dying]

                low = (vals <= 0.75)
                high = (vals > 0.75)

                if np.any(low):
                    rr, cc = rows[low], cols[low]
                    intensity = vals[low]
                    color[rr, cc, 0] = (255 * intensity).astype(np.uint8)
                    color[rr, cc, 1] = 0
                    color[rr, cc, 2] = 0

                if np.any(high):
                    rr, cc = rows[high], cols[high]
                    intensity = (vals[high] - 0.5) * 2
                    color[rr, cc, 0] = 255
                    color[rr, cc, 1] = (165 * intensity).astype(np.uint8)
                    color[rr, cc, 2] = 0

        return color

    
    def start(self, tick=0, verbose=2):
        self.gameboard.start_window()
        display = self.gameboard.display

        is_running = True
        dt = pygame.time.Clock()

        grid_surface = pygame.Surface((self.w, self.h))
        scaled_surface = pygame.Surface((self.display_w, self.display_h))

        while is_running:
            tick = (tick + 1) % 100
            
            # check for quitting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.active
                        self.active = not self.active
                    elif event.key == pygame.K_r:
                        self.add_random_life()
                    elif event.key == pygame.K_e:
                        self.adding_life = not self.adding_life

            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                x, y = pygame.mouse.get_pos()
                self.add_life(x, y)

            if self.active and tick % verbose == 0:
                self.update()

            # crazy-ahh drawing logic
            color = self.grid_to_color()
            color_transpose = np.transpose(color, (1, 0, 2))
            pygame.surfarray.blit_array(grid_surface, color_transpose)
            pygame.transform.scale(grid_surface, (self.display_w, self.display_h), scaled_surface)
            display.blit(scaled_surface, (0,0))
            pygame.display.flip()

            dt.tick(self.FPS)

    

if __name__ == '__main__':
    g = GameOfLife()
    g.start()

    # pygame.init()
    # simulation = GameOfLife()
    # framerate = 60
    # activeRate = 30
    # verbose = framerate // activeRate
    # tick = 0
    # WHITE = (255, 255, 255)
    # BLACK = (0, 0, 0)
    # display = pygame.display.set_mode((simulation.display_w, simulation.display_h))
    # clock = pygame.time.Clock()
    # active = True
    # while active:
    #     tick = (tick + 1) % 100
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             active = False
    #         elif event.type == pygame.KEYDOWN:
    #             if event.key == pygame.K_SPACE:
    #                 simulation.active = not simulation.active
    #             elif event.key == pygame.K_r:
    #                 simulation.add_random_life()
    #             elif event.key == pygame.K_e:
    #                 simulation.adding_life = not simulation.adding_life
                    
    #     pressed = pygame.mouse.get_pressed()
    #     if pressed[0]:
    #         x, y = pygame.mouse.get_pos()
    #         simulation.add_life(x, y)

    #     if simulation.active and (tick % verbose == 0):
    #         simulation.update()

    #     color = simulation.grid_to_color()
    #     color_transpose = np.transpose(color, (1, 0, 2))
    #     grid_surface = pygame.Surface((simulation.w, simulation.h))
    #     scaled_surface = pygame.Surface((simulation.display_w, simulation.display_h))
    #     pygame.surfarray.blit_array(grid_surface, color_transpose)
    #     pygame.transform.scale(grid_surface, (simulation.display_w, simulation.display_h), scaled_surface)
    #     display.blit(scaled_surface, (0,0))
    #     pygame.display.flip()
        

    #     clock.tick(framerate)