
import turtle as t
import time
start = time.time()

LENGTH = 80
A = 30

t.colormode(255)
t.tracer(0,0)
tre = t.Turtle()

# recursive function
def tree(n, s=LENGTH):
    if n > 0:
        tre.pencolor(int(255/n),0,0)
        tre.pensize(n)
        tre.fd(s)
        # left branch
        tre.lt(A)
        tree(n-1, 0.8*s)
        tre.pencolor(int(255/n),0,0)
        tre.pensize(n)
        # right branch
        tre.rt(2*A)
        tree(n-1, 0.8*s)
        tre.pencolor(int(255/n),0,0)
        tre.pensize(n)
        tre.lt(A)
        tre.fd(-s)

tre.pu()
tre.goto(0, -170)
tre.lt(90)
tre.pd()
tree(14, LENGTH)

end = time.time()
tre.pu()
tre.setpos(-250, 230)
tre.pencolor(0,0,0)
tre.write("Time: " + str(round(end-start, 4)) + " seconds", False, align="left", font=("Arial", 20, "normal"))

t.exitonclick()