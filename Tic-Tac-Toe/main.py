
import turtle as t
import random

# set up the turtle
SIZE = int(input("Enter the board size (around 200-500): "))
t.hideturtle()
t.speed(0)
t.pu()

# make the grid
cells = [[0,0,0],[0,0,0],[0,0,0]]
# each inner list represents a row
# 0 is empty, 1 is X, and 2 is O

def grid(SIZE):
    # set up and go to the correct location
    t.speed(0)
    t.pensize(5)
    SPACE = SIZE / 3
    t.setpos(-SIZE/2, SIZE/2)
    # make the columns
    for i in range(4):
        t.setheading(270)
        t.pd()
        t.fd(SIZE)
        t.pu()
        t.setpos(-SIZE/2+SPACE*(i+1), SIZE/2)
    # make the rows
    t.setpos(-SIZE/2, SIZE/2)
    for i in range(4):
        t.setheading(0)
        t.pd()
        t.fd(SIZE)
        t.pu()
        t.setpos(-SIZE/2, SIZE/2-SPACE*(i+1))


# cross function
def cross(userPos):
    # go the the center of the square
    POS = SIZE / 3
    pos = [(userPos[1]-1) * POS, -(userPos[0]-1) * POS]
    t.setpos(pos)
    crossLen = 0.15 * SIZE
    # make the cross
    t.pd()
    t.color("red")
    for i in range(2):
        t.setheading(45 + 90*i)
        t.fd(crossLen)
        t.bk(2*crossLen)
        t.fd(crossLen)
    t.setheading(0)
    t.color("black")
    t.pu()

# zero function
def zero(userPos):
    # go slightly below the center of the square
    circLen = 0.08 * SIZE
    POS = SIZE / 3
    pos = [(userPos[1]-1) * POS, -(userPos[0]-1) * POS - (circLen)]
    t.setpos(pos)
    # create the circle
    t.pd()
    t.color("blue")
    t.circle(circLen)
    t.color("black")
    t.pu()
    

# check if position is taken or not
def getPos():
    # ask for a square until the location is good
    good = False
    while not good:
        userRcor = int(input("What row will you go in (1, 2, or 3): "))
        userCcor = int(input("what column will you go in (1, 2, or 3): "))
        x, y = userRcor-1, userCcor-1
        if cells[x][y] > 0:
            print("This is not a valid spot!")
            continue
        else:
            good = True
            cells[x][y] = 1
            return x, y


# computer's turn
def computer():
    good = False
    while not good:
        x = random.randint(1,3) - 1
        y = random.randint(1,3) - 1
        if cells[x][y] > 0:
            continue
        else:
            good = True
            cells[x][y] = 2
            zero([x,y])
            print("computer went in row " + str(x+1) + " and column " + str(y+1))


# victory or tie function
def win(cells):
    # check 'cells' for a winner
    # check columns
    for i in range(3):
        if cells[i][0] == cells[i][1] == cells[i][2] and (cells[i][0] != 0):
            if cells[i][0] == 1:
                winner = "You"
            else:
                winner = "Computer"
            return winner

    # check rows
    for i in range(3):
        if cells[0][i] == cells[1][i] == cells[2][i] and (cells[0][i] != 0):
            if cells[i][0] == 1:
                winner = "You"
            else:
                winner = "Computer"
            return winner
    # check diagonals
    # diagonal one
    if cells[0][0] == cells[1][1] == cells[2][2] and (cells[0][0] != 0):
        if cells[0][0] == 1:
            winner = "You"
        else:
            winner = "Computer"
        return winner
    # diagonal two
    if cells[0][2] == cells[1][1] == cells[2][0] and (cells[0][2] != 0):
        if cells[0][2] == 1:
            winner = "You"
        else:
            winner = "Computer"
        return winner
    
    # check for tie
    open = False
    for i in cells:
        if 0 in i:
            open = True
    if open == False:
        winner = "Tie"
        return winner
    return False

# win result
def result(winner):
    done = None
    running = 'y'
    winner = win(cells)
    if winner == "Computer":
        done = True
        print("Computer won!")
        running = input("play again? (y/n): ")

    elif winner == "You":
        done = True
        print("You won!")
        running = input("play again? (y/n): ")

    elif winner == "Tie":
        done = True
        print("Tie!")
        running = input("play again? (y/n): ")
    return [done, running, winner]


# recreate board function
def clear(yes=True):
    t.clearscreen()
    t.pu()
    if yes:
        grid(SIZE)
    t.pu()
    global cells
    cells = [[0,0,0],[0,0,0],[0,0,0]]


# game loop
running = "y"
while running == "y":
    # clear the board
    clear()
    # while no one has one yet
    done = False
    while not done:
        # ask user for Cross position
        x, y = getPos()
        cells[x][y] = 1
        # place Cross
        cross([x,y])
        # check for winner
        check = result(win(cells))
        done = check[0]
        running = check[1]
        winner = check[2]
        if winner is not False:
            break

        # computer randomly puts an O
        computer()
        print(cells)
        # check for winner
        check = result(win(cells))
        done = check[0]
        running = check[1]
        winner = check[2]
        

if running != 'y':
    clear(False)
    print("ok...")

t.exitonclick()