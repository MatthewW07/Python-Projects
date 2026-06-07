# Catch a Turtle - Python
# Author: Matthew Wang
# Program is a game that gives the user 15 seconds to click the red dot as much as possible
#-----import statements--------

from itertools import count
import turtle as t
import random as r

#-----game configuration--------
# Turtle/Spot variables:
FILL_COLOR = "red"
SIZE = 3
SHAPE = "circle"
# Score:
score = 0
# Font:
font_setup = ("Georgia", 20, "normal")
# Timer:
timer = 15
counter_interval = 1000
timer_up = False

#-----initialize turtle---------

# Create and Configure 'spot':
spot = t.Turtle()
spot.pu()
spot.speed(0)
spot.shape(SHAPE)
spot.shapesize(SIZE)
spot.fillcolor(FILL_COLOR)
# Create and Configure 'score_writer':
score_writer = t.Turtle()
score_writer.speed(0)
score_writer.pu()
score_writer.hideturtle()
score_writer.goto(200,240)
# Create and Configure 'counter':
counter = t.Turtle()
counter.speed(0)
counter.pu()
counter.hideturtle()
counter.goto(-280,240)

#-----game functions------------

def spot_clicked(x, y):
    # literally does what the function names say
    global timer_up
    if not timer_up:
        change_position()
        update_score()
    else:
        spot.hideturtle()

def change_position():
    # BOARD SIZE: 
    # -400 <= x <= 400
    # -300 <= y <= 300
    x = r.randint(-360, 360) # Select x coor within board but not on edge
    y = r.randint(-260, 260) # Select y coor within board but not on edge
    new_Xpos = x
    new_Ypos = y
    # Disappear and reappear at new location
    spot.hideturtle()
    spot.goto(new_Xpos, new_Ypos)
    spot.showturtle()

def update_score():
    global score
    score += 1
    score_writer.clear()
    score_writer.write("Score: " + str(score), font=font_setup)

def countdown():
    global timer, timer_up
    counter.clear()
    if timer <= 0:
        counter.write("Time's up!", font=font_setup)
        timer_up = True
    else:
        counter.write("Timer: " + str(timer), font=font_setup)
        timer -= 1
        counter.getscreen().ontimer(countdown, counter_interval)


#-----events-------------------

wn = t.Screen()
wn.ontimer(countdown, counter_interval)
spot.onclick(spot_clicked) # call spot_clicked when 'spot' is clicked.

wn.mainloop()