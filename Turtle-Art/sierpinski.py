
import turtle as t
import time
start = time.time()

LENGTH = 500

t.tracer(0,0)
tri = t.Turtle()
tri.pu()

# base function
def base(s):
    tri.pd()
    x = tri.xcor()
    y = tri.ycor()
    tri.setpos(x+s, y)
    tri.setpos(x+0.5*s, y+0.866*s)
    tri.setpos(x,y)
    tri.pu()

# recursive function
def sier(n, s=LENGTH):
    if n == 1:
        base(s)
    else:
        x = tri.xcor()
        y = tri.ycor()
        sier(n-1,s/2)
        tri.setpos(x+s/2,y)
        sier(n-1,s/2)
        tri.setpos(x+s/4,y+0.433*s)
        sier(n-1,s/2)
        tri.setpos(x,y)

# setup
tri.pu()
tri.goto(-LENGTH/2, -LENGTH/2)
tri.pd()
sier(8)

end = time.time()
tri.setpos(-250, 230)
tri.write("Time: " + str(round(end-start, 4)) + " seconds", False, align="left", font=("Arial", 20, "normal"))

t.exitonclick()