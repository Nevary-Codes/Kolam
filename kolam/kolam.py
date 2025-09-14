import turtle
from tkinter import simpledialog
from PIL import Image
import os

def draw_kolam(rows, cols, spacing, loop_radius, save_name="kolam.png"):
    # Setup turtle screen
    screen = turtle.Screen()
    screen.title("Kolam Generator")
    screen.bgcolor("white")
    screen.setup(width=800, height=600)
    
    pen = turtle.Turtle()
    pen.speed(0)
    pen.pensize(2)
    pen.color("blue")

    start_x = - (cols - 1) * spacing // 2
    start_y = (rows - 1) * spacing // 2

    # Draw dots
    pen.penup()
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * spacing
            y = start_y - r * spacing
            pen.goto(x, y)
            pen.dot(6, "black")

    # Draw loops (simple kolam)
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * spacing
            y = start_y - r * spacing
            pen.penup()
            pen.goto(x, y - loop_radius)
            pen.pendown()
            pen.circle(loop_radius)

    # Save the drawing as PostScript
    ts = pen.getscreen().getcanvas()
    ts.postscript(file="kolam_tmp.eps")

    # Convert EPS to PNG
    img = Image.open("kolam_tmp.eps")
    img.save(save_name, "PNG")

    # Clean up
    os.remove("kolam_tmp.eps")
    print(f"✅ Kolam saved as {save_name}")

    screen.mainloop()


if __name__ == "__main__":
    # Get user inputs
    rows = simpledialog.askinteger("Input", "Enter number of rows:", minvalue=1, maxvalue=10)
    cols = simpledialog.askinteger("Input", "Enter number of cols:", minvalue=1, maxvalue=10)
    spacing = simpledialog.askinteger("Input", "Enter spacing between dots (e.g., 50):", minvalue=20, maxvalue=100)
    loop_radius = simpledialog.askinteger("Input", "Enter loop radius (e.g., 20):", minvalue=5, maxvalue=50)

    draw_kolam(rows, cols, spacing, loop_radius, save_name="kolam.png")