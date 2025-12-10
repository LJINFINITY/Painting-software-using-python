import tkinter as tk
import tkinter.colorchooser as cc
from tkinter import filedialog as fd
from PIL import Image, ImageDraw, ImageTk
from collections import deque

ms=""  #Mouse State
mdx=mdy=mux=muy=0 #Temp cords for drawing shapes and stuff
lx=ly=0  #Last Mouse cords
bs=2    #Brush Size
bc="#000000"  #Brush Color
ct="brush"      #Current Tool
ts=None     #Tool Shape

us=[]  #undo stack
rs=[]  #redo stack

W, H = 1200, 800  
img = Image.new("RGB", (W, H), "white")
us.append(img.copy())
draw = ImageDraw.Draw(img)

def ei():
    fp=fd.asksaveasfile(defaultextension=".png",
                        filetypes=(("PNG", "*.png"), 
                                   ("JPEG", "*.jpg")))
    if fp:
        img.save(fp.name)

def uc():
    global tk_img
    tk_img = ImageTk.PhotoImage(img)
    c.itemconfig(img_id, image=tk_img)

def ff(x, y, fill_color):
    start_color = img.getpixel((x, y))
    if start_color == fill_color:
        return

    q = deque()
    q.append((x, y))

    while q:
        px, py = q.pop()
        if px < 0 or py < 0 or px >= W or py >= H:
            continue
        if img.getpixel((px, py)) != start_color:
            continue
        img.putpixel((px, py), fill_color)
        q.append((px+1, py))
        q.append((px-1, py))
        q.append((px, py+1))
        q.append((px, py-1))
    uc()

def nc(x1, y1, x2, y2):
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
def hex_to_rgb(h):
    
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def dt(x, y):
    global bc, bs, ct, ts, ms

    if ct == "brush" and ms in ["down", "move"]:
        draw.line((lx, ly, x, y), fill=bc, width=bs*2,joint="smooth")
        draw.ellipse((lx-bs+2, ly-bs+2, lx+bs-2, ly+bs-2), fill=bc)
        uc()
    elif ct == "eraser" and ms in ["down", "move"]:
        draw.line((lx, ly, x, y), fill="white", width=bs*2,joint="smooth")
        draw.ellipse((lx-bs+2, ly-bs+2, lx+bs-2, ly+bs-2), fill="white")
        uc()
    elif ct == "fill" and ms == "down":
        ff(x, y, hex_to_rgb(bc))
    elif ct == "circle" and ms == "move":
        c.delete(ts)
        tx1,ty1,tx2,ty2 = nc(mdx, mdy, x, y)
        ts = c.create_oval(tx1, ty1, tx2, ty2, outline=bc, fill="")
    elif ct == "circle" and ms == "up":
        c.delete(ts)
        draw.ellipse(nc(mdx, mdy, x, y), fill=bc, outline=bc)
        uc()
    elif ct == "rectangle" and ms == "move":
        c.delete(ts)
        tx1,ty1,tx2,ty2 = nc(mdx, mdy, x, y)
        ts = c.create_rectangle(tx1, ty1, tx2, ty2, outline=bc, fill="")
    elif ct == "rectangle" and ms == "up":
        c.delete(ts)
        draw.rectangle(nc(mdx, mdy, x, y), fill=bc, outline=bc)
        uc()

def md(event):
    global mdx, mdy, lx, ly, ms
    ms = "down"
    mdx, mdy = event.x, event.y
    lx, ly = event.x, event.y
    dt(event.x, event.y)
    
def mm(event):
    global lx, ly, ms
    ms = "move"
    dt(event.x, event.y)
    lx, ly = event.x, event.y

def mu(event):
    global ms, draw,lx,ly
    lx=ly=0
    ms = "up"
    dt(event.x, event.y)
    us.append(img.copy())
    rs.clear()

def undo():
    global us, rs, img, draw
    if len(us) > 1:
        rs.append(us.pop())
        img = us[-1]
        draw = ImageDraw.Draw(img)
        uc()

def redo():
    global us, rs, img, draw
    if rs:
        img = rs.pop()
        us.append(img.copy())
        draw = ImageDraw.Draw(img)
        uc()
        
def set_bs(x):
    global bs
    bs = int(x)

def set_bc():
    global bc
    color = cc.askcolor()[1]
    if color: bc = color

def set_ct(x):
    global ct
    ct = x

r = tk.Tk()
r.focus_set()
r.title("Painting App")
r.state("zoomed")

tb = tk.Frame(r)
tb.pack(side="left", fill="y")

tk.Scale(tb, from_=1, to=30, orient="horizontal",
         label="Brush Size", command=set_bs).pack(pady=5)

tk.Button(tb, text="Choose Color", command=set_bc).pack(pady=5)
tk.Button(tb, text="Brush", command=lambda: set_ct("brush")).pack(pady=5)
tk.Button(tb, text="Eraser", command=lambda: set_ct("eraser")).pack(pady=5)
tk.Button(tb, text="Fill", command=lambda: set_ct("fill")).pack(pady=5)
tk.Button(tb, text="Circle", command=lambda: set_ct("circle")).pack(pady=5)
tk.Button(tb, text="Rectangle", command=lambda: set_ct("rectangle")).pack(pady=5)
tk.Button(tb, text="💾 Export Image", command=ei).pack(pady=5)

c = tk.Canvas(r, bg="white")
c.pack(fill="both", expand=True)

tk_img = ImageTk.PhotoImage(img)
img_id = c.create_image(0, 0, anchor="nw", image=tk_img)

c.bind("<Button-1>", md)
c.bind("<B1-Motion>", mm)
c.bind("<ButtonRelease-1>", mu)
r.bind_all("<Control-z>", lambda e: undo())
r.bind_all("<Control-Z>", lambda e: redo())

r.mainloop()
