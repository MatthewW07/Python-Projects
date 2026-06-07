import numpy as np
import pygame
import rings as rings

class GameBoard:
    def __init__(self, size=(800, 800)):
        self.size = size

    def start_window(self):
        pygame.init()
        pygame.display.set_caption("One-Neighbor Cellular Automata")
        self.display = pygame.display.set_mode(self.size)
        self.surface = pygame.Surface(self.size)


class OneNeighbor:
    def __init__(self, w=250, h=250, TILESIZE=2, FPS=60):
        self.w = w
        self.h = h
        self.TILESIZE = 2
        self.FPS = FPS
        self.display_w = self.w * self.TILESIZE
        self.display_h = self.h * self.TILESIZE
        self.gameboard = GameBoard(size=(self.display_w, self.display_h))
        self.grid = np.zeros((self.h, self.w), dtype=np.float32)
        self.running = False
        self.trail = True
        self.alive_threshold = 0.99
        self.dying_weight = 0.5
        self.decay = 0.1
        self.random_life = False
        self.adding_life = True
        self.draw_radius = 2

    def add_life(self, x, y):
        if (x < 0) or (x >= self.display_w):
            return
        if (y < 0) or (y >= self.display_h):
            return
        x //= self.TILESIZE
        y //= self.TILESIZE
        if self.adding_life:
            self.grid[max(0, y-self.draw_radius):min(self.h, y+self.draw_radius+1), max(0, x-self.draw_radius):min(self.w, x+self.draw_radius+1)] = 1.0
        else:
            self.grid[max(0, y-self.draw_radius):min(self.h, y+self.draw_radius+1), max(0, x-self.draw_radius):min(self.w, x+self.draw_radius+1)] = 0.0

    def update(self):
        g = self.grid.astype(np.float32)
        new_grid = np.where(g < self.alive_threshold, np.maximum(0.0, g - self.decay), g)

        # Neighborhood 1
        cur_rings = [1,2,3,4,5]
        sums = (rings.check_rings(
            cur_rings, self.grid, self.w, self.h, 
            self.alive_threshold, 
            self.random_life, 
            dist_type="chebyshev", 
            averages=False
        ))

        new_grid[(0 <= sums[0]) & (sums[0] <= 33)] -= self.decay
        new_grid[(34 <= sums[0]) & (sums[0] <= 45)] = 1.0
        new_grid[(58 <= sums[0]) & (sums[0] <= 121)] -= self.decay

        self.grid = new_grid


    def grid_to_color(self):
        color = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        if not self.trail:
            alive = (self.grid == 1.0)
            color[alive] = [255, 200, 150]
        else:
            alive = (self.grid == 1.0)
            color[alive] = [255, 200, 150]

            dying = ((self.grid > 0.0) & (self.grid < 1.0))
            dying_values = self.grid[dying]

            low_dying = (dying_values <= 0.75)
            high_dying = (dying_values > 0.75)

            if np.any(low_dying):
                # The (rows: array, cols: array) tuple from np.where(dying) is aligned with the bool array low_dying
                low_indices = np.where(dying)[0][low_dying], np.where(dying)[1][low_dying]
                intensity = dying_values[low_dying]
                color[low_indices[0], low_indices[1], 0] = (255 * intensity).astype(np.uint8)
                color[low_indices[0], low_indices[1], 1] = 0
                color[low_indices[0], low_indices[1], 2] = 0

            if np.any(high_dying):
                high_indices = np.where(dying)[0][high_dying], np.where(dying)[1][high_dying]
                intensity = (dying_values[high_dying] - 0.5) * 2
                color[high_indices[0], high_indices[1], 0] = 255
                color[high_indices[0], high_indices[1], 1] = (165 * intensity).astype(np.uint8)
                color[high_indices[0], high_indices[1], 2] = 0

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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.running = not self.running
                    elif event.key == pygame.K_e:
                        self.adding_life = not self.adding_life
                    elif event.key == pygame.K_r:
                        self.random_life = not self.random_life
                    elif event.key == pygame.K_t:
                        self.trail = not self.trail
                    elif event.unicode.isdigit():
                        self.draw_radius = int(event.unicode)

            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                x, y = pygame.mouse.get_pos()
                self.add_life(x, y)

            if self.running and (tick % verbose == 0):
                self.update()

            color_array = self.grid_to_color()
            color_transpose = np.transpose(color_array, (1, 0, 2))
            
            pygame.surfarray.blit_array(grid_surface, color_transpose)
            pygame.transform.scale(grid_surface, (self.display_w, self.display_h), scaled_surface)
            display.blit(scaled_surface, (0,0))
            pygame.display.flip()

            dt.tick(self.FPS)



if __name__ == '__main__':
    on = OneNeighbor()
    on.start()
