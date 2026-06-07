import pygame
import random
import numpy as np

pygame.init()

# RGB Colors
LIGHT_GREEN = (153, 200, 66)    # Unknown 1
LIGHTER_GREEN = (170, 215, 81)  # Unknown 2
LIGHT_BROWN = (215, 184, 153)   # Revealed 1
LIGHTER_BROWN = (229, 194, 159) # Revealed 2
DARK_GRAY = (128, 128, 128)     # Dark Gray
RED = (255, 0, 0)               # Mine
BLUE = (0, 0, 255)              # Click
GREEN = (0, 255, 0)             # Flag
TEXT_COLORS = {
    1: (25, 118, 210),
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: (136, 34, 87),
    5: (193, 0, 60),
    6: (106, 13, 173),
    7: (0, 0, 0),
    8: (128, 128, 128)
}


# Game Constants
SPEED = 2
TILE_SIZE = 40
HALF_TILE = TILE_SIZE // 2
FLAG_RADIUS = 6
NUM_MINES = 10


class MinesweeperAI:
    def __init__(self, w=9, h=9):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w * TILE_SIZE, self.h * TILE_SIZE))
        pygame.display.set_caption("Minesweeper")
        self.board = [[-1 for _ in range(w)] for _ in range(h)]
        self.mines = set()
        self.hidden_space = w * h - NUM_MINES
        self.clock = pygame.time.Clock()
        self.render = True
        self.clicks = 0
        self.reset()
        self._update_ui()

    def reset(self):
        self.board = [[-1 for _ in range(self.w)] for _ in range(self.h)]
        self.mines = set()
        self.clicks = 0
        self.hidden_space = self.w * self.h - NUM_MINES
        pygame.time.delay(1000)
        self._update_ui()
        # 10 is mine
        # -1 is unknown
        # 0 is clear
        # 1-8 is number of mines

    def play_step(self, pt):
        x, y = pt
        if self.clicks == 0: 
            self._load_mines(pt, NUM_MINES)
        self.clicks += 1

        # 1: Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.render = not self.render

        # 2: Perform action
        self._check_point(pt)
        if self.render:
            pygame.draw.circle(self.display, BLUE, (x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE), FLAG_RADIUS)
            pygame.display.flip()
            
        # 3: Check if game over
        done = 0
        if self.board[y][x] == 10:
            done = -1
        elif self.hidden_space == 0:
            done = 1

        # 4: Update UI
        if self.render:
            self._update_ui()
            self.clock.tick(SPEED)
        else:
            pygame.event.pump()

        # 5: Return reward & done
        return done

    def _check_point(self, pt):
        x, y = pt
        if pt in self.mines:
            self.board[y][x] = 10
        else:
            def count_mines(pt):
                x, y = pt
                res = 0
                for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                    if (x + dx, y + dy) in self.mines:
                        res += 1
                return res

            visited = set()
            queue = []
            queue.append(pt)

            while queue:
                cur = queue.pop(0)
                x, y = cur
                if cur in visited or self.board[y][x] != -1:
                    continue
                visited.add(cur)
                self.board[y][x] = count_mines(cur)
                self.hidden_space -= 1
                if self.board[y][x] == 0:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                        if 0 <= x + dx < self.w and 0 <= y + dy < self.h:
                            queue.append((x + dx, y + dy))
                
    def _load_mines(self, start_point, num_mines):
        while len(self.mines) < num_mines:
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            # need to have start_point clear at the start, so no mines there are around it
            if abs(x - start_point[0]) <= 1 and abs(y - start_point[1]) <= 1:
                continue
            if (x, y) not in self.mines:
                self.mines.add((x, y))

    def _update_ui(self):
        self.display.fill(DARK_GRAY)

        for y in range(self.h):
            for x in range(self.w):
                
                if self.board[y][x] == 10:
                    pygame.draw.rect(self.display, RED, pygame.Rect(x * TILE_SIZE + 1, y * TILE_SIZE + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                elif self.board[y][x] == -1:
                    if (x % 2 == y % 2):
                        pygame.draw.rect(self.display, LIGHTER_GREEN, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    else:
                        pygame.draw.rect(self.display, LIGHT_GREEN, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    if (x % 2 == y % 2):
                        pygame.draw.rect(self.display, LIGHTER_BROWN, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    else:
                        pygame.draw.rect(self.display, LIGHT_BROWN, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    if self.board[y][x] > 0:
                        font = pygame.font.SysFont('courier', 36, bold=True)
                        text = font.render(str(self.board[y][x]), True, TEXT_COLORS[self.board[y][x]])
                        text_rect = text.get_rect(center=(x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE))
                        self.display.blit(text, text_rect)
                    
        pygame.display.flip()

    def get_observation(self):
        numbers = np.zeros((self.h, self.w), dtype=np.float32)
        unknown_mask = np.ones((self.h, self.w), dtype=np.float32)
        for y in range(self.h):
            for x in range(self.w):
                v = self.board[y][x]
                if v == -1:
                    numbers[y, x] = 0.0
                    unknown_mask[y, x] = 1.0
                elif v == 10:
                    numbers[y, x] = 1.0
                    unknown_mask[y, x] = 0.0
                else:
                    numbers[y, x] = v / 8.0
                    unknown_mask[y, x] = 0.0
        obs = np.stack([numbers, unknown_mask], axis=0)
        return obs
    
    def available_actions(self):
        actions = []
        for y in range(self.h):
            for x in range(self.w):
                if self.board[y][x] == -1:
                    actions.append((x, y))
        return actions
    
    def step(self, pt):
        done = self.play_step(pt)
        if self.board[pt[1]][pt[0]] == 10:
            reward = -1.0
        else:
            reward = 0.05
            if self.hidden_space == 0:
                reward = 1.0
        obs = self.get_observation()
        return obs, reward, done



# Code to make the file a playable game for a human
if __name__ == '__main__':
    pygame.init()
    game = MinesweeperAI()
    
    # game loop
    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x //= TILE_SIZE
                y //= TILE_SIZE
                pt = (x, y)
                done = game.play_step(pt)
                if done == -1:
                    print("Game over!")
                    game.reset()
                elif done == 1:
                    print("You won!")
                    game.reset()
        
    pygame.quit()
