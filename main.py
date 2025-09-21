import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle
import matplotlib
matplotlib.use("Agg")   # ✅ Use a headless backend (no GUI)
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle


# ---------------- Base Dot Grid ----------------
def draw_dot_grid(ax, rows, cols, spacing=1.0, dot_radius=0.05, dot_color="black"):
    xs = np.arange(cols) * spacing
    ys = np.arange(rows) * spacing
    for y in ys:
        for x in xs:
            c = Circle((x, y), dot_radius, color=dot_color)
            ax.add_patch(c)
    return xs, ys

# ---------------- Weave Kolam ----------------
# ---- Weave styles registry ----
weave_styles = {
    "classic": lambda i,j: [(180,270),(0,90)] if (i+j)%2==0 else [(90,180),(270,360)],
    "checkerboard": lambda i,j: [(0,90),(180,270)] if (i+j)%2==0 else [(90,180),(270,360)],
    "lines": lambda i,j: [(0,180)] if (i+j)%2==0 else [(180,360)],
    "diagonal": lambda i,j: [(45,135)] if (i+j)%2==0 else [(225,315)],
    "cross": lambda i,j: [(0,180),(90,270)],
    "zigzag": lambda i,j: [(0,90),(270,360)] if (i%2==0) else [(90,180),(180,270)],
    "concentric": lambda i,j: [(0, 360)] if (i+j)%2==0 else [(45,135),(225,315)],
    "spiral-weave": lambda i,j: [(0+(i*30)%360, 180+(i*30)%360)],
    "horizontal": lambda i,j: [(0,180)],
    "vertical": lambda i,j: [(90,270)],
    "diamond": lambda i,j: [(45,135),(225,315)] if (i+j)%2==0 else [(135,225),(315,45)],
    "circle-grid": lambda i,j: [(0,360)] if (i+j)%2==0 else [],
    "star": lambda i,j: [(0,90),(90,180),(180,270),(270,360)] if (i+j)%2==0 else [],
    "offset-diagonal": lambda i,j: [(30,150)] if (i+j)%2==0 else [(210,330)],
    "wave": lambda i,j: [(0,180)] if i%2==0 else [(180,360)],
    "petal": lambda i,j: [(0,90),(90,180),(180,270),(270,360)],
}

def kolam_weave(ax, rows=9, cols=9, spacing=1.0,
                line_color="black", line_width=1.5, style="classic"):
    xs = np.arange(cols) * spacing
    ys = np.arange(rows) * spacing
    style_func = weave_styles.get(style, weave_styles["classic"])

    for i in range(cols-1):
        for j in range(rows-1):
            cx, cy = xs[i] + spacing/2, ys[j] + spacing/2
            arcs = style_func(i, j)
            for (t1, t2) in arcs:
                ax.add_patch(
                    Arc((cx, cy), spacing, spacing,
                        theta1=t1, theta2=t2,
                        color=line_color, lw=line_width)
                )

    ax.set_xlim(-spacing, (cols-1)*spacing + spacing)
    ax.set_ylim(-spacing, (rows-1)*spacing + spacing)

# ---------------- Radial Kolam ----------------
def kolam_radial(ax, n_petals=8, rings=3, radius=1.0, line_color="black", line_width=1.5, ring_scale=0.8):
    theta = np.linspace(0, 2*np.pi, 1000)
    for m in range(1, rings+1):
        k = n_petals + m
        r = radius * (1 + 0.3*np.cos(k*theta)) * (ring_scale**(m-1))
        ax.plot(r*np.cos(theta), r*np.sin(theta), color=line_color, lw=line_width)

# ---------------- Fractal Kolam ----------------
def kolam_fractal(ax, depth=4, size=1.0, line_color="black", line_width=1.0):
    def draw_square(x,y,s,d):
        ax.plot([x-s,x+s,x+s,x-s,x-s],
                [y-s,y-s,y+s,y+s,y-s],
                color=line_color, lw=line_width)
        if d>0:
            new_s = s/2
            draw_square(x+s,y,new_s,d-1)
            draw_square(x-s,y,new_s,d-1)
            draw_square(x,y+s,new_s,d-1)
            draw_square(x,y-s,new_s,d-1)
    draw_square(0,0,size,depth)

# ---------------- Spiral Kolam ----------------
def kolam_spiral(ax, turns=6, spacing=0.3, line_color="black", line_width=1.5):
    theta = np.linspace(0, 2*np.pi*turns, 2000)
    r = spacing * theta
    ax.plot(r*np.cos(theta), r*np.sin(theta), color=line_color, lw=line_width)

# ---------------- Mandala Kolam ----------------
def kolam_mandala(ax, layers=5, petals=8, radius=1.0, line_color="black", line_width=1.5):
    theta = np.linspace(0, 2*np.pi, 1000)
    for m in range(1, layers+1):
        r = radius * (1 + 0.3*np.cos(petals*m*theta)) * (0.8**(m-1))
        ax.plot(r*np.cos(theta), r*np.sin(theta), color=line_color, lw=line_width)

# ---------------- Lattice Kolam ----------------
def kolam_lattice(ax, rows=9, cols=9, spacing=1.0, line_color="black", line_width=1.5):
    xs = np.arange(cols) * spacing
    ys = np.arange(rows) * spacing
    for x in xs:
        ax.plot([x, x], [ys[0], ys[-1]], color=line_color, lw=line_width)
    for y in ys:
        ax.plot([xs[0], xs[-1]], [y, y], color=line_color, lw=line_width)

# ---------------- Flower Kolam ----------------
def kolam_flower(ax, petals=8, radius=1.0, line_color="black", line_width=1.5):
    theta = np.linspace(0, 2*np.pi, 1000)
    r = radius * np.sin(petals*theta)
    ax.plot(r*np.cos(theta), r*np.sin(theta), color=line_color, lw=line_width)

# ---------------- API: Generate Image ----------------
def generate_kolam_image(pattern="weave",
                         rows=9, cols=9,
                         n_petals=8, rings=3,
                         spacing=1.0, radius=1.5,
                         dot_grid=True, dot_radius=0.05,
                         line_color="black", dot_color="black", bg_color="white",
                         line_width=1.5, weave_style="classic",
                         fractal_depth=3, ring_scale=0.8,
                         turns=6, layers=5, petals=8):
    fig, ax = plt.subplots(figsize=(6,6), facecolor=bg_color)

    if pattern == "weave":
        kolam_weave(ax, rows, cols, spacing, line_color, line_width, weave_style)
        if dot_grid:
            draw_dot_grid(ax, rows, cols, spacing, dot_radius, dot_color)

    elif pattern == "radial":
        kolam_radial(ax, n_petals, rings, radius, line_color, line_width, ring_scale)

    elif pattern == "fractal":
        kolam_fractal(ax, fractal_depth, radius, line_color, line_width)

    elif pattern == "spiral":
        kolam_spiral(ax, turns=turns, spacing=spacing, line_color=line_color, line_width=line_width)

    elif pattern == "mandala":
        max_r = radius * layers * 0.7   # maximum reach of mandala
        for layer in range(1, layers + 1):
            r = radius * layer * 0.7
            for i in range(n_petals * layer):
                angle = 2 * np.pi * i / (n_petals * layer)
                x = r * np.cos(angle)
                y = r * np.sin(angle)
                circle = plt.Circle((x, y), r * 0.2, 
                                    fill=False, 
                                    color=line_color, 
                                    linewidth=line_width)
                ax.add_patch(circle)

        # ✅ Ensure mandala is fully visible
        ax.set_xlim(-max_r * 1.2, max_r * 1.2)
        ax.set_ylim(-max_r * 1.2, max_r * 1.2)



    elif pattern == "lattice":
        kolam_lattice(ax, rows=rows, cols=cols, spacing=spacing,
                      line_color=line_color, line_width=line_width)

    elif pattern == "flower":
        kolam_flower(ax, petals=n_petals, radius=radius,
                     line_color=line_color, line_width=line_width)

    ax.set_aspect("equal")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200, facecolor=bg_color)
    plt.close(fig)
    buf.seek(0)
    return buf
