from Tkinter import Tk, Canvas, ALL

width = 400
height = 300
ow = 10

master = Tk()
w = Canvas(master, width=width, height=height, bg="#2222AA")
w.pack()

selected = [ [0] * (height/ow ) for _ in xrange(width/ow)]

def step(t):
    d = t%20
    for i in xrange(d):
        selected[i][d] = d/20.0
    
def redraw(t=0, fps=20):
    w.delete(ALL)
    step(t)

    for x in xrange(width/ow):
        for y in xrange(height/ow):            
            fill = '#{0:02x}{0:02x}{0:02x}'.format(int(selected[x][y] * 0xff))
            draw_x = 1 + x * ow
            draw_y = 1 + y * ow
            w.create_rectangle(draw_x, draw_y, draw_x + ow, draw_y + ow, fill=fill)
    
    dt = 1000/fps
    master.after(dt, redraw, t + 1)

redraw()
master.mainloop()