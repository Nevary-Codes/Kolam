import streamlit as st
from main import generate_kolam_image, weave_styles

st.title("🎨 Customizable Kolam Art Generator")

# Step 1: choose pattern type
pattern = st.selectbox("Kolam Pattern", ["weave", "radial", "fractal", "spiral", "mandala", "lattice", "flower"])

# Common customizations
line_color = st.color_picker("Line Color", "#000000")
dot_color = st.color_picker("Dot Color", "#000000")
bg_color = st.color_picker("Background Color", "#FFFFFF")
line_width = st.slider("Line Width", 1.0, 5.0, 1.5)
buf = None

# ---------------- Pattern-specific settings ----------------
if pattern == "weave":
    rows = st.slider("Rows", 3, 15, 9)
    cols = st.slider("Columns", 3, 15, 9)
    spacing = st.slider("Spacing", 0.5, 2.0, 1.0)
    weave_style = st.selectbox("Weave Style", list(weave_styles.keys()))
    dot_grid = st.checkbox("Show Dot Grid", True)
    buf = generate_kolam_image(
        pattern="weave", rows=rows, cols=cols, spacing=spacing,
        line_color=line_color, line_width=line_width,
        weave_style=weave_style, dot_grid=dot_grid,
        dot_color=dot_color, bg_color=bg_color
    )

elif pattern == "radial":
    n_petals = st.slider("Number of Petals", 4, 20, 8)
    rings = st.slider("Number of Rings", 1, 10, 3)
    radius = st.slider("Radius", 0.5, 5.0, 1.5)
    ring_scale = st.slider("Ring Scale", 0.5, 0.95, 0.8)
    buf = generate_kolam_image(
        pattern="radial", n_petals=n_petals, rings=rings, radius=radius,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color, ring_scale=ring_scale
    )

elif pattern == "fractal":
    depth = st.slider("Fractal Depth", 1, 6, 3)
    radius = st.slider("Base Size", 0.5, 3.0, 1.5)
    buf = generate_kolam_image(
        pattern="fractal", fractal_depth=depth, radius=radius,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color
    )

elif pattern == "spiral":
    turns = st.slider("Turns", 3, 20, 6)
    buf = generate_kolam_image(
        pattern="spiral", turns=turns,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color
    )

elif pattern == "mandala":
    layers = st.slider("Layers", 1, 10, 5)
    n_petals = st.slider("Petals", 4, 20, 8)
    buf = generate_kolam_image(
        pattern="mandala", layers=layers, n_petals=n_petals,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color
    )

elif pattern == "lattice":
    rows = st.slider("Rows", 3, 20, 9)
    cols = st.slider("Columns", 3, 20, 9)
    buf = generate_kolam_image(
        pattern="lattice", rows=rows, cols=cols,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color
    )

elif pattern == "flower":
    n_petals = st.slider("Petals", 4, 20, 8)
    buf = generate_kolam_image(
        pattern="flower", n_petals=n_petals,
        line_color=line_color, line_width=line_width,
        bg_color=bg_color
    )

# ---------------- Display Output ----------------
if buf:
    st.image(buf, caption=f"{pattern.capitalize()} Kolam", use_container_width=True)
