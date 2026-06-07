"""
Asteroid Game:
The user is located in space, where asteroids appear every 4 seconds
The user must shoot these asteroids by pressing 's'
The user can move: right with 'd', left with 'a', and forward with 'w'
"""

# I made this a while ago, so I had ChatGPT revise it to be more OOP-style
# the logic used is the same though

import turtle as t
import random
import math

# Variables -----------

STAR_COUNT = 60
ASTEROID_SPEED = 1
ASTEROID_START_RATE = 4000
ASTEROID_MIN_RATE = 1500
PLAYER_SPEED = 2
LASER_SPEED = 10
TURN_SPEED = 7
FPS = 20
GAME_OVER = False

level = 0
point = 0

# Objects ------------

class Player:
    def __init__(self, screen):
        self.turtle = t.Turtle()
        self.turtle.color("white")
        self.turtle.pencolor("white")
        self.turtle.shape("arrow")
        self.turtle.pensize(3)
        self.turtle.pu()
        self.turtle.goto(0, 0)
        self.turtle.setheading(90)

    def move_forward(self):
       self.turtle.forward(PLAYER_SPEED)

    def turn_right(self):
       self.turtle.right(TURN_SPEED)

    def turn_left(self):
       self.turtle.left(TURN_SPEED)


class Asteroid:
    def __init__(self, player):
        self.turtle = t.Turtle()
        self.turtle.shape("circle")
        self.turtle.shapesize(3)
        self.turtle.color("orange")
        self.turtle.penup()

        x = random.choice(list(range(100, 480)) + list(range(-480, -100)))
        y = random.choice(list(range(100, 330)) + list(range(-330, -100)))
        self.turtle.goto(x, y)

        dx = player.turtle.xcor() - x
        dy = player.turtle.ycor() - y
        heading = math.degrees(math.atan2(dy, dx))
        self.turtle.setheading(heading)

        self.alive = True

    def move(self, speed):
        if self.alive:
            self.turtle.forward(speed)

    def hide(self):
        self.alive = False
        self.turtle.hideturtle()


class Laser:
    def __init__(self, player):
        self.turtle = t.Turtle()
        self.turtle.penup()
        self.turtle.color("blue")
        self.turtle.pencolor("blue")
        self.turtle.shape("circle")
        self.turtle.shapesize(0.3, 0.3)
        self.turtle.goto(player.turtle.position())
        self.turtle.setheading(player.turtle.heading())

    def move(self):
        self.turtle.forward(LASER_SPEED)

    def off_screen(self):
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        return x < -520 or x > 520 or y < -370 or y > 370

    def destroy(self):
        self.turtle.hideturtle()


# Game ------------

class Game:
    def __init__(self):
        self.screen = t.Screen()
        self.screen.setup(600, 500)
        self.screen.bgcolor("black")
        self.screen.tracer(False)

        self.player = Player(self.screen)
        self.asteroids = []
        self.lasers = []

        self.star_pen = t.Turtle()
        self.star_pen.hideturtle()
        self.star_pen.penup()
        self.star_pen.color("white")
        self.star_pen.pensize(1)

        self.info_pen = t.Turtle()
        self.info_pen.hideturtle()
        self.info_pen.penup()
        self.info_pen.color("white")

        self.game_over_pen = t.Turtle()
        self.game_over_pen.hideturtle()
        self.game_over_pen.penup()

        self.movement = {"fd": False, "lt": False, "rt": False}

        self.level = 0
        self.score = 0
        self.asteroid_rate = ASTEROID_START_RATE
        self.asteroid_speed = ASTEROID_SPEED
        self.game_over = False

        self.draw_stars()
        self.show_tutorial()
        self.setup_controls()


    def draw_stars(self):
        self.star_pen.clear()
        for _ in range(STAR_COUNT):
            x = random.randint(-480, 480)
            y = random.randint(-330, 330)
            self.star_pen.goto(x, y)
            self.star_pen.dot(2, "white")


    def show_tutorial(self):
        tut = t.Turtle()
        tut.color("blue")
        tut.penup()
        tut.hideturtle()

        tut.goto(0, 90)
        tut.write("W -> Forward", align="center", font=("Georgia", 20, "normal"))
        tut.goto(0, 30)
        tut.write("A -> Left", align="center", font=("Georgia", 20, "normal"))
        tut.goto(0, -30)
        tut.write("D -> Right", align="center", font=("Georgia", 20, "normal"))
        tut.goto(0, -90)
        tut.write("SPACE -> Shoot", align="center", font=("Georgia", 20, "normal"))

        self.screen.update()
        self.screen.ontimer(tut.clear, 3000)


    def setup_controls(self):
        self.screen.listen()

        self.screen.onkeypress(self.right, "d")
        self.screen.onkeypress(self.left, "a")
        self.screen.onkeypress(self.forward, "w")
        self.screen.onkeypress(self.shoot, " ")

        self.screen.onkeyrelease(self.right_stop, "d")
        self.screen.onkeyrelease(self.left_stop, "a")
        self.screen.onkeyrelease(self.forward_stop, "w")

    def right(self):
        self.movement["rt"] = True

    def left(self):
        self.movement["lt"] = True

    def forward(self):
        self.movement["fd"] = True

    def right_stop(self):
        self.movement["rt"] = False

    def left_stop(self):
        self.movement["lt"] = False

    def forward_stop(self):
        self.movement["fd"] = False

    def shoot(self):
        if self.game_over:
            return
        self.lasers.append(Laser(self.player))
        if len(self.lasers) == 1:
            self.move_lasers()

    def spawn_asteroid(self):
        if self.game_over:
            return

        asteroid = Asteroid(self.player)
        self.asteroids.append(asteroid)

        self.level += 1

        if self.level % 5 == 0:
            self.asteroid_rate = max(ASTEROID_MIN_RATE, self.asteroid_rate - 100)

        if self.level % 8 == 0:
            self.asteroid_speed = min(6, self.asteroid_speed + 1)

        self.screen.update()
        self.screen.ontimer(self.spawn_asteroid, self.asteroid_rate)


    def move_asteroids(self):
        if self.game_over:
            return

        for asteroid in self.asteroids:
            asteroid.move(self.asteroid_speed)

        self.check_collisions()
        self.screen.update()
        self.screen.ontimer(self.move_asteroids, 20)


    def move_lasers(self):
        if self.game_over:
            return

        i = 0
        while i < len(self.lasers):
            laser = self.lasers[i]
            laser.move()

            hit_index = None
            for j, asteroid in enumerate(self.asteroids):
                if asteroid.alive and laser.turtle.distance(asteroid.turtle) < 40:
                    hit_index = j
                    break

            if hit_index is not None:
                self.asteroids[hit_index].hide()
                laser.destroy()
                self.lasers.pop(i)
                self.score += 1
                continue

            if laser.off_screen():
                laser.destroy()
                self.lasers.pop(i)
                continue

            i += 1

        self.screen.update()

        if self.lasers:
            self.screen.ontimer(self.move_lasers, 20)


    def check_collisions(self):
        for asteroid in self.asteroids:
            if asteroid.alive and self.player.turtle.distance(asteroid.turtle) < 40:
                self.end_game()
                break


    def end_game(self):
        self.game_over = True

        for asteroid in self.asteroids:
            asteroid.hide()
        for laser in self.lasers:
            laser.destroy()

        self.game_over_pen.goto(0, 250)
        self.game_over_pen.color("red")
        self.game_over_pen.write(
            "GAME OVER!",
            align="center",
            font=("Georgia", 20, "normal")
        )

        self.game_over_pen.goto(0, 200)
        self.game_over_pen.write(
            f"You shot {self.score} asteroids!",
            align="center",
            font=("Georgia", 20, "normal")
        )

        self.screen.onkeypress(None, "w")
        self.screen.onkeypress(None, "a")
        self.screen.onkeypress(None, "d")
        self.screen.onkeypress(None, "s")

    
    def move_player(self):
        if self.game_over:
            return

        if self.movement["fd"]:
            self.player.move_forward()
        if self.movement["rt"]:
            self.player.turn_right()
        if self.movement["lt"]:
            self.player.turn_left()

        self.screen.update()
        self.screen.ontimer(self.move_player, 30)


    def start(self):
        self.spawn_asteroid()
        self.move_asteroids()
        self.move_player()
        self.screen.exitonclick()


# Run --------

if __name__ == "__main__":
    game = Game()
    game.start()
