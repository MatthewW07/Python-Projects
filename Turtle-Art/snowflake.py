
import turtle as t
import time
start = time.time()

LENGTH = 400

t.tracer(0,0)
sqr = t.Turtle()

# base function
def base(s):
    sqr.fd(s)

# recursive function
def square(n, s=LENGTH):
    if n == 1:
        base(s)
    else:
        square(n-1,s/3)
        sqr.lt(60)
        square(n-1,s/3)
        sqr.rt(120)
        square(n-1,s/3)
        sqr.lt(60)
        square(n-1,s/3)

def snowflake(n, s=LENGTH):
    sqr.setheading(60)
    square(n, s)
    sqr.setheading(300)
    square(n, s)
    sqr.setheading(180)
    square(n, s)
    sqr.setheading(0)

sqr.pu()
sqr.goto(-LENGTH/2, -170)
sqr.pd()
snowflake(8, LENGTH)

end = time.time()
sqr.pu()
sqr.setpos(-250, 230)
sqr.write("Time: " + str(round(end-start, 4)) + " seconds", False, align="left", font=("Arial", 20, "normal"))

t.exitonclick()