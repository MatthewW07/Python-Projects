import pygame
import random

# put all the computational logic stuff here


class GameBoard:
    # visual representation of the game board
    # don't do the logic here, this is mainly where the graphics are handled

    def __init__(self, size=(800, 800)):
        self.size = size

    def startWindow(self):
        pygame.init()
        pygame.display.set_caption("Quick Start")
        window_surface = pygame.display.set_mode(self.size)

        self.background = pygame.Surface(self.size)
        self.background.fill(pygame.Color("#000000"))
        self.window_surface = window_surface


class Cell:
    # a cell on the game board

    def __init__(self, position, size=(5, 5)):
        self.position = position
        self.size = size
        self.status = 1  # 1 for alive, 0 for dead

    def findNeighbors(self, cells, radius):
        aliveCellsInRadius = []

        for cell in cells:
            # check absolute distance
            if (
                abs(cell.position[0] - self.position[0]) <= radius
                and abs(cell.position[1] - self.position[1]) <= radius
            ):
                if cell.status == 1:
                    aliveCellsInRadius.append(cell)
        return aliveCellsInRadius


class GameOfLife:
    # making our game of life object
    # this is the parent object that controls everything else
    # it has a game board and a list of cells
    def __init__(self, size=(800, 800), units=100, FPS=60):
        # initialize our game of life object
        self.gameboard = GameBoard(size)
        self.units = units
        self.cells = []
        self.FPS = FPS

    def generate_cells(self):
        # generate the cells for the game board
        # make possible_colors red, green or blue in hex
        cell_size = [5, 5]
        for x in range(self.units):
            # random position on the game board
            position = [
                random.randint(0, self.gameboard.size[0]),
                random.randint(0, self.gameboard.size[1]),
            ]
            # random color from the possible_colors list
            # create a cell object
            cell = Cell(position, cell_size)
            # add the cell to the list of cells
            self.cells.append(cell)

    def update(self):
        population_change = False
        # apply the rules of the game of life to the cells
        # this is where the logic is
        for cell1 in self.cells:
            aliveNeighbors = cell1.findNeighbors(self.cells, 35)
            # now implement some rules
            # if cell1 is alive and has less than 2 neighbors, cell1 dies
            # if cell1 is alive and has 2 or 3 neighbors, cell1 stays alive
            # if cell1 is alive and has more than 3 neighbors, cell1 dies
            # if cell1 is dead and has 3 neighbors, cell1 comes to life
            # cell1.position[0] += random.randint(-1, 1)
            # cell1.position[1] += random.randint(-1, 1)
            if cell1.status == 1:
                if len(aliveNeighbors) < 2:
                    cell1.status = 0
                    population_change = True
                elif len(aliveNeighbors) > 3:
                    cell1.status = 0
                    population_change = True
            else:
                if len(aliveNeighbors) == 3:
                    cell1.status = 1
                    population_change = True
            if not population_change:
                for cell in self.cells:
                    cell.position[0] += random.randint(-1, 1)
                    cell.position[1] += random.randint(-1, 1)

    def start(self, manual=False):
        # start the game
        self.gameboard.startWindow()
        self.generate_cells()
        window_surface = self.gameboard.window_surface
        background = self.gameboard.background

        is_running = True
        dt = pygame.time.Clock()

        while is_running:

            # CHECK IF USER QUITS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                # now update the game
                if manual:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.update()
            if not manual:
                self.update()

            # re-draw everything
            window_surface.blit(background, (0, 0))
            for cell in self.cells:
                # the color should be based on the status of the cell
                # white for alive, black for dead
                color = None
                if cell.status == 1:
                    color = pygame.Color("#ffffff")
                else:
                    color = pygame.Color("#000000")

                pygame.draw.rect(
                    window_surface,
                    color,
                    (cell.position[0], cell.position[1], cell.size[0], cell.size[1]),
                )
            pygame.display.update()
            dt.tick(self.FPS)


g = GameOfLife(FPS=15, units=500)
g.start(manual=False)