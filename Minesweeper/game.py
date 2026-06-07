import pygame
import random

pygame.init()

# RGB Colors
LIGHT_GRAY = (216, 216, 216)    # Revealed Area
DARK_GRAY = (128, 128, 128)     # Unknown Area
RED = (255, 0, 0)               # Mine
BLUE = (0, 0, 255)              # Click
GREEN = (0, 255, 0)             # Flag


# Game Constants
SPEED = 2
TILE_SIZE = 20
HALF_TILE = 10
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
        self.flagged = set()
        self.clock = pygame.time.Clock()
        self.render = True
        self.clicks = 0
        self.reset()
        self._update_ui()

    def reset(self):
        self.board = [[-1 for _ in range(self.w)] for _ in range(self.h)]
        self.mines = set()
        self._load_mines((0, 0), NUM_MINES)
        self.clicks = 0
        self.flagged = set()
        # -3 is mine
        # -2 is flag
        # -1 is unknown
        # 0 is clear
        # 1-8 is number of mines

    def play_step(self, action, pt):
        #print("Action:", action, "Point:", pt)
        x, y = pt
        # 1: Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.render = not self.render

        # 2: Perform action (flag or reveal)
        reward = 0
        if action == -1: # flag
            if self.render:
                pygame.draw.circle(self.display, GREEN, (x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE), FLAG_RADIUS)
                pygame.display.flip()
            if pt in self.mines:
                reward += 1
                self.board[y][x] = -2
                self.flagged.add(pt)
            else:
                reward -= 5
                self.board[y][x] = -2
                self.flagged.add(pt)

        elif action == 1: # reveal
            if self.render:
                pygame.draw.circle(self.display, BLUE, (x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE), FLAG_RADIUS)
                pygame.display.flip()
            reward = 2
            self.clicks += 1
            self._check_point(pt)
            if self.board[y][x] > 0:
                reward += self.clicks * 2
            
        # 3: Check if game over
        done = False
        if self.board[y][x] == -3:
            done = True
            reward = -20
        elif self.hidden_space == 0:
            done = True
            reward = 100

        # 4: Update UI
        if self.render:
            self._update_ui()
            self.clock.tick(SPEED)
        else:
            pygame.event.pump()

        # 5: Return reward & done
        return reward, done

    def _check_point(self, pt):
        x, y = pt
        if pt in self.mines:
            self.board[y][x] = -3
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
                self.hidden_space -= 1
                self.board[y][x] = count_mines(cur)
                if self.board[y][x] == 0:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if 0 <= x + dx < self.w and 0 <= y + dy < self.h:
                            queue.append((x + dx, y + dy))
                
    def _load_mines(self, start_point, num_mines):
        while len(self.mines) < num_mines:
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            # need to have start_point clear at the start, so no mines there are around it
            if abs(x - start_point[0] <= 1) and (abs(y - start_point[1] <= 1)):
                continue
            if (x, y) not in self.mines:
                self.mines.add((x, y))

    def _update_ui(self):
        self.display.fill(DARK_GRAY)

        for y in range(self.h):
            for x in range(self.w):
                
                if self.board[y][x] == -3:
                    pygame.draw.rect(self.display, RED, pygame.Rect(x * TILE_SIZE + 1, y * TILE_SIZE + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                elif self.board[y][x] == -2:
                    pygame.draw.rect(self.display, DARK_GRAY, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    pygame.draw.circle(self.display, RED, (x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE), FLAG_RADIUS)
                elif self.board[y][x] == -1:
                    pygame.draw.rect(self.display, DARK_GRAY, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif self.board[y][x] == 0:
                    pygame.draw.rect(self.display, DARK_GRAY, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.display, LIGHT_GRAY, pygame.Rect(x * TILE_SIZE + 1, y * TILE_SIZE + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                else:
                    pygame.draw.rect(self.display, DARK_GRAY, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.display, LIGHT_GRAY, pygame.Rect(x * TILE_SIZE + 1, y * TILE_SIZE + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                    font = pygame.font.SysFont('courier', 15, bold=True)
                    text = font.render(str(self.board[y][x]), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(x * TILE_SIZE + HALF_TILE, y * TILE_SIZE + HALF_TILE))
                    self.display.blit(text, text_rect)

        pygame.display.flip()

#"""
# Human playable game
if __name__ == '__main__':
    game = MinesweeperAI()
    
    # game loop
    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    action = "reveal"
                elif event.button == 3:
                    action = "flag"
                x, y = event.pos
                x //= TILE_SIZE
                y //= TILE_SIZE
                pt = (x, y)
                reward, game_over = game.play_step(action, pt)
                print("Reward", reward)
                print("Done", game_over)
                print("Hidden space", game.hidden_space)
        
    pygame.quit()
#"""