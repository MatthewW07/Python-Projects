import pygame
import numpy as np

pygame.init()

BLACK = (0, 0, 0)
BLUE = (16, 32, 64)
LIGHT_BLUE = (12, 88, 188)
WHITE = (255, 255, 255)

class Drawing:
    def __init__(self, model, grid=(28, 28), framerate=100, bottomHeight=100, sideWidth=220, tileSize=15):
        self.framerate = framerate
        self.bottomHeight = bottomHeight
        self.sideWidth = sideWidth
        self.tileSize = tileSize
        self.grid = grid
        self.model = model
        self.w = self.grid[1] * self.tileSize
        self.h = self.grid[0] * self.tileSize
        self.image = np.zeros((self.grid[0], self.grid[1]))
        self.display = pygame.display.set_mode((self.w + self.sideWidth, self.h + self.bottomHeight))
        self.trainButton = pygame.Rect(self.w + 20, self.h + 20, self.sideWidth - 40, 40)
        self.labelButtons = [pygame.Rect(self.w + 20, 20 + i * 40, self.sideWidth - 40, 40) for i in range(10)]
        self.clock = pygame.time.Clock()
        self.sortedPairs = []
        self.curLabel = np.zeros(10)
        self.curLabel[0] = 1
        pygame.display.set_caption("Drawing Digits")

    def main(self):
        self.render_ui()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.image = np.zeros((self.grid[0], self.grid[1]))
                        self.render_ui()
                    elif event.key == pygame.K_z:
                        self.train()
                    elif event.unicode.isdigit():
                        self.curLabel = np.zeros(10)
                        self.curLabel[int(event.unicode)] = 1
                        self.render_ui()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.trainButton.collidepoint(pygame.mouse.get_pos()):
                            self.train()
                        else:
                            x, y = pygame.mouse.get_pos()
                            for i in range(len(self.labelButtons)):
                                labelButton = self.labelButtons[i]
                                if labelButton.collidepoint((x, y)):
                                    idx = self.sortedPairs[i][0]
                                    self.curLabel = np.zeros(10)
                                    self.curLabel[idx] = 1
                                    self.render_ui()
                                    print("Label: ", self.curLabel)
                                    continue


            pressed = pygame.mouse.get_pressed()
            if pygame.mouse.get_pos()[0] < self.w and pygame.mouse.get_pos()[1] < self.h:
                if pressed[0]:
                    x, y = pygame.mouse.get_pos()
                    x //= self.tileSize
                    y //= self.tileSize
                    self.draw(x, y, add=True)
                    self.render_ui()
                elif pressed[2]:
                    x, y = pygame.mouse.get_pos()
                    x //= self.tileSize
                    y //= self.tileSize
                    self.draw(x, y, add=False)
                    self.render_ui()
                elif pressed[1]:
                    self.image = np.zeros((self.grid[0], self.grid[1]))
                    self.render_ui()

            self.clock.tick(self.framerate)
        pygame.quit()

    def train(self):
        print("Training:")
        print("Label: ", self.curLabel)
        for i in range(5):
            self.model.learn(0.01, [self.image.reshape(784, 1)], [self.curLabel])
        self.render_ui()


    def draw(self, x, y, add=True):
        DIAGS = 0.04
        EDGES = 0.08
        POINT = 0.8

        # Point
        if (x < 0 or x >= 28) or (y < 0 or y >= 28):
            return self.image
        if add:
            self.image[y][x] = min(1, self.image[y][x] + POINT)
        else:
            self.image[y][x] = 0


        # Edges
        for dx, dy in ((0, 1), (-1, 0), (1, 0), (0, -1), ):
            posX = x + dx
            posY = y + dy
            if (posX < 0 or posX >= 28) or (posY < 0 or posY >= 28):
                continue
            if add:
                self.image[posY][posX] = min(1, self.image[posY][posX] + EDGES)
            else:
                #self.image[posY][posX] = max(0, self.image[posY][posX] - EDGES)
                self.image[posY][posX] = 0
        # Diagonals
        for dx, dy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
            posX = x + dx
            posY = y + dy
            if (posX < 0 or posX >= 28) or (posY < 0 or posY >= 28):
                continue
            if add:
                self.image[posY][posX] = min(1, self.image[posY][posX] + DIAGS)
            else:
                #self.image[posY][posX] = max(0, self.image[posY][posX] - DIAGS)
                self.image[posY][posX] = 0
                pass

    def render_ui(self):
        self.display.fill(BLACK)

        # 1: render image
        for y in range(self.grid[0]):
            for x in range(self.grid[1]):
                val = self.image[y][x] * 255
                color = (val, val, val)
                topLeftY = y * self.tileSize
                topLeftX = x * self.tileSize
                rect = pygame.Rect(topLeftX, topLeftY, self.tileSize, self.tileSize)
                pygame.draw.rect(self.display, color, rect)

        # 2: render Outputs
        bottomLeft = (0, self.grid[0] * self.tileSize)
        bottomRight = (self.grid[1] * self.tileSize, self.grid[0] * self.tileSize)
        topRight = (self.grid[1] * self.tileSize, 0)
        width = 5
        pygame.draw.line(self.display, BLUE, bottomLeft, bottomRight, width)
        pygame.draw.line(self.display, BLUE, topRight, bottomRight, width)

        # confidences
        probs = np.ones(10) / 10.0
        predictionOutput = self.model.predict(self.image)
        probs = np.asarray(predictionOutput, dtype=float).ravel()
        probs = probs / probs.sum()
        percents = (probs * 100.0)
        topPred = int(np.argmax(probs))
        pairs = sorted([(i, float(percents[i])) for i in range(10)], key=lambda t: t[1], reverse=True)
        self.sortedPairs = pairs

        bigFont = pygame.font.SysFont('courier', 24, bold=True)
        medFont = pygame.font.SysFont('courier', 18, bold=True)

        predText = bigFont.render("Prediction: " + str(topPred), True, (255, 255, 255))
        predTextRect = pygame.Rect(20, bottomLeft[1] + 20, self.w // 2 - 20, self.h // 2 - 20)
        self.display.blit(predText, predTextRect)

        num = np.argmax(self.curLabel)
        pairsX = self.w + 30
        pairsY = 20
        for i in range(len(pairs)):
            digit, percent = pairs[i]
            label = medFont.render(f"{digit}:  " + f"{percent:.2f}%", True, WHITE)
            labelButton = self.labelButtons[i]
            if digit == num:
                pygame.draw.rect(self.display, LIGHT_BLUE, labelButton)
            pygame.draw.rect(self.display, BLUE, labelButton, 1)
            self.display.blit(label, (pairsX, pairsY + 10 + i * 40))
        
        # 3: Train button
        pygame.draw.rect(self.display, BLUE, self.trainButton)
        trainText = medFont.render("Train", True, WHITE)
        trainTextRect = trainText.get_rect(center=self.trainButton.center)
        self.display.blit(trainText, trainTextRect)

        # 4: Update
        pygame.display.flip()

    def render_outputs(self):
        pass
