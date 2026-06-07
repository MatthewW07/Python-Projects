import pygame
import random

EMPTY_COLOR = (0, 200, 255)

WIDTH = 600
HEIGHT = 500
CELL = 10
ROWS = HEIGHT // CELL
COLS = WIDTH // CELL


#make 2d arraay
def make2Darray(rows, cols, initial=0):
    return [ [initial for j in range(rows)] for i in range(cols) ]



#update function
def update(canvas, grid):
    new_grid = [row[:] for row in grid]

    for col in range(COLS):
        for row in range(ROWS):

            if grid[col][row] > 0:
            
                # reached bottom
                if (row == ROWS - 1) or (grid[col][row+1] > 0):
                    new_grid[col][row] = grid[col][row]
                    color = (grid[col][row], 0, 0)
                    
                elif (grid[col][row+1] == 0):
                    new_grid[col][row+1] = grid[col][row]
                    new_grid[col][row] = 0
                    color = (grid[col][row], 0, 0)
            
            elif grid[col][row] == 0:
                color = EMPTY_COLOR
            
            pygame.draw.rect(canvas, color, (col * CELL, row * CELL, CELL, CELL))
    
    return new_grid
        




#main function
def main():
    pygame.init()
    pygame.display.set_caption("My Falling Sand")

    canvas = pygame.display.set_mode((WIDTH, HEIGHT))
    grid = make2Darray(ROWS, COLS)
    clock = pygame.time.Clock()
    HUE = 100

    update(canvas, grid)

    pygame.display.flip()
    pygame.display.update()

    while True:
        # COLOR
        HUE += 2
        if HUE > 240:
            HUE = 100

        for event in pygame.event.get():
            # the quit option
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # the create option
            elif pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                grid[pos[0] // CELL][pos[1] // CELL] = HUE
                if (0 < pos[0] // CELL < COLS - 1):
                    grid[pos[0] // CELL + 1][pos[1] // CELL] = HUE
                    grid[pos[0] // CELL - 1][pos[1] // CELL] = HUE
                if (0 < pos[1] // CELL < ROWS - 1):
                    #grid[pos[0] // CELL][pos[1] // CELL + 1] = HUE
                    grid[pos[0] // CELL][pos[1] // CELL - 1] = HUE
                update(canvas, grid)
                pygame.display.update()


        grid = update(canvas, grid)
        pygame.display.update()

        clock.tick(30)


if __name__ == '__main__':
    main()