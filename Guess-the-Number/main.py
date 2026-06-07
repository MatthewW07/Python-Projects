import random

running = "y"
while running == "y":
    number = random.randint(0,100)
    guesses = 0
    guess = None
    while guess != number:
        guess = input("Guess a number 1-100 : ")
        try:
            guess = int(guess)
        except ValueError:
            guess = int(input("Give a valid integer: "))

        if guess == number:
            print("You got it in " + str(guesses) + "!")
        elif guess > number:
            print("Too high!")
        elif guess < number:
            print("Too low!")
        guesses += 1

    running = input("Play again? (y/n) : ")