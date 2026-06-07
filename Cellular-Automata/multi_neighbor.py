import numpy as np
import pygame
import rings as rings
import slider as Slider


class GameBoard:
    def __init__(self, size=(800, 800)):
        self.size = size

    def start_window(self):
        pygame.init()
        pygame.display.set_caption("Multi-Neighbor Cellular Automata")
        self.display = pygame.display.set_mode(self.size)
        self.surface = pygame.Surface(self.size)


class MultiNeighbor:
    def __init__(self, w=300, h=300, TILESIZE=2, FPS=60):
        self.ui_w = 200
        self.w = w
        self.h = h
        self.TILESIZE = TILESIZE
        self.FPS = FPS
        self.display_w = self.w * self.TILESIZE
        self.display_h = self.h * self.TILESIZE
        self.gameboard = GameBoard(size=(self.display_w + self.ui_w, self.display_h))
        self.grid = np.zeros((self.h, self.w), dtype=np.float32)
        self.active = False
        self.trail = False
        self.decay = 0.05
        self.alive_threshold = 0.96
        self.dying_weight = 0.5
        self.random_life = False
        self.adding_life = True
        self.draw_radius = 2
        self.ring_weights = {1: 1, 2: 0.9, 3: 0.8, 4: 0.7, 5: 0.6, 6: 0.5, 7: 0.4, 8: 0.3, 9: 0.2, 10: 0.1}


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
        new_grid = np.where(self.grid < self.alive_threshold, np.maximum(0.0, self.grid - self.decay), self.grid)

        n0 = rings.check_rings([5, 6, 7], self.grid, self.w, self.h, self.alive_threshold)
        n1 = rings.check_rings([1, 2, 3], self.grid, self.w, self.h, self.alive_threshold)


        # Two neigborhoods: n[0] = [5, 6, 7] and n[1] = [1, 2, 3].
        # n[0] Life: [0.185, 0.200] => x = 1.0
        # n[0] Decay: [0.343, 0.58] U [0.75, 0.85] => x -= self.decay
        # n[1] Life: [0.445, 0.68] => x = 1.0
        # n[1] Decay: [0.159, 0.28] => self.decay
        # n = (
        #     rings.check_rings([5,6,7], self.grid, self.w, self.h, self.alive_threshold, self.random_life), 
        #     rings.check_rings([1,2,3], self.grid, self.w, self.h, self.alive_threshold, self.random_life)
        # )
        new_grid[(0.210 <= n0) & (n0 <= 0.220)] = 1.0
        new_grid[(0.350 <= n0) & (n0 <= 0.500)] -= self.decay
        new_grid[(0.750 <= n0) & (n0 <= 0.850)] -= self.decay
        new_grid[(0.100 <= n1) & (n1 <= 0.280)] -= self.decay
        new_grid[(0.430 <= n1) & (n1 <= 0.550)] = 1.0
        new_grid[(0.120 <= n0) & (n0 <= 0.150)] -= self.decay

        self.grid = new_grid


    def add_random_life(self):
        new_life = 500
        rows = np.random.randint(0, self.h, new_life)
        cols = np.random.randint(0, self.w, new_life)
        self.grid[rows, cols] = 1.0


    def grid_to_color(self):
        color = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        alive = (self.grid == 1.0)
        color[alive] = [150, 255, 200]
        
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
                    color[rr, cc, 0] = 0
                    color[rr, cc, 1] = 0
                    color[rr, cc, 2] =  (255 * intensity).astype(np.uint8)

                if np.any(high):
                    rr, cc = rows[high], cols[high]
                    intensity = (vals[high] - 0.5) * 2 
                    color[rr, cc, 0] = 0
                    color[rr, cc, 1] = (165 * intensity).astype(np.uint8)
                    color[rr, cc, 2] = 255

        return color
    

    def start(self, tick=0, verbose=2):
        self.gameboard.start_window()
        display = self.gameboard.display

        is_running = True
        dt = pygame.time.Clock()

        ui_left = self.display_w
        pad = 20
        slider_w = self.ui_w - pad * 2

        decay_rect = pygame.Rect(ui_left + pad, 20, slider_w, 30)
        alive_rect = pygame.Rect(ui_left + pad, 100, slider_w, 30)

        decay_slider = Slider.Slider(decay_rect, 0.0, 1.0, self.decay)
        alive_slider = Slider.Slider(alive_rect, 0.0, 1.0, self.alive_threshold)
        sliders = [decay_slider, alive_slider]
        font = pygame.font.Font(None, 20)

        grid_surface = pygame.Surface((self.w, self.h))
        scaled_surface = pygame.Surface((self.display_w, self.display_h))

        while is_running:
            tick = (tick + 1) % 100

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    break
                for s in sliders:
                    s.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.active = not self.active
                    elif event.key == pygame.K_e:
                        self.adding_life = not self.adding_life
                    elif event.key == pygame.K_r:
                        self.random_life = not self.random_life
                    elif event.key == pygame.K_t:
                        self.trail = not self.trail
                    elif event.key == pygame.K_a:
                        self.add_random_life()
                    elif event.unicode.isdigit():
                        self.draw_radius = int(event.unicode)

            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                x, y = pygame.mouse.get_pos()
                if x < self.display_w:
                    self.add_life(x, y)

            try:
                self.decay = float(decay_slider.value)
                self.alive_threshold = float(alive_slider.value)
            except Exception:
                pass

            if self.active and (tick % verbose == 0):
                self.update()

            # level 100 coloring book type stuff
            color_array = self.grid_to_color()
            color_transpose = np.transpose(color_array, (1, 0, 2))
            pygame.surfarray.blit_array(grid_surface, color_transpose)
            pygame.transform.scale(grid_surface, (self.display_w, self.display_h), scaled_surface)
            display.blit(scaled_surface, (0,0))

            ui_rect = pygame.Rect(self.display_w, 0, self.ui_w, self.display_h)
            pygame.draw.rect(display, (30,30,30), ui_rect)

            for label, s in (("decay", decay_slider), ("alive_thr", alive_slider)):
                try:
                    s.draw(display)
                except Exception:
                    pass

                val_text = f"{label}: {float(s.value):.3f}"
                text_surf = font.render(val_text, True, (220, 220, 220))
                text_y = s.rect.y + s.rect.height + 8 if hasattr(s, "rect") else 0
                display.blit(text_surf, (s.rect.x, text_y))

            pygame.display.flip()
            dt.tick(self.FPS)


if __name__ == '__main__':
    mn = MultiNeighbor()
    mn.start()
