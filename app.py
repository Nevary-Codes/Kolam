import base64
import io
import cv2
from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for
import os
from matplotlib import pyplot as plt
import numpy as np
from torch import device
import torch
from kolam.style_transfer import load_image, run_style_transfer, tensor_to_pil
from main import generate_kolam_image, weave_styles
from kolam.analysis import analyze_and_plot_kolam, analyze_kolam_full_phone

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/kolam")
def kolam():
    return render_template("kolam.html", weave_styles=weave_styles.keys())


@app.route("/generate_kolam", methods=["POST"])
def generate_kolam():

    # Extract options (with defaults matching your function)
    pattern = request.form.get("pattern", "weave")
    rows = int(request.form.get("rows", 9))
    cols = int(request.form.get("cols", 9))
    n_petals = int(request.form.get("n_petals", 8))
    rings = int(request.form.get("rings", 3))
    spacing = float(request.form.get("spacing", 1.0))
    radius = float(request.form.get("radius", 1.5))
    dot_grid = bool(request.form.get("dot_grid", True))
    dot_radius = float(request.form.get("dot_radius", 0.05))
    line_color = request.form.get("line_color", "black")
    dot_color = request.form.get("dot_color", "black")
    bg_color = request.form.get("bg_color", "white")
    line_width = float(request.form.get("line_width", 1.5))
    weave_style = request.form.get("weave_style", "classic")
    fractal_depth = int(request.form.get("fractal_depth", 3))
    ring_scale = float(request.form.get("ring_scale", 0.8))
    turns = int(request.form.get("turns", 6))
    layers = int(request.form.get("layers", 5))
    petals = int(request.form.get("petals", 8))

    # ✅ Call your function
    buf = generate_kolam_image(
        pattern=pattern,
        rows=rows, cols=cols,
        n_petals=n_petals, rings=rings,
        spacing=spacing, radius=radius,
        dot_grid=dot_grid, dot_radius=dot_radius,
        line_color=line_color, dot_color=dot_color, bg_color=bg_color,
        line_width=line_width, weave_style=weave_style,
        fractal_depth=fractal_depth, ring_scale=ring_scale,
        turns=turns, layers=layers, petals=petals
    )

    return send_file(buf, mimetype="image/png")
    # return redirect(url_for(kolam))

@app.route("/principles")
def principles():
    return render_template("principles.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Save temporarily
    image_path = "temp_kolam.jpg"
    file.save(image_path)

    # 1️⃣ Left pane: analyzed image using analyze_and_plot_kolam
    dots_left, skeleton_left = analyze_and_plot_kolam(
        image_path, dot_size=5, skeleton_marker_size=1, skeleton_color='gray'
    )
    # Convert the matplotlib figure from analyze_and_plot_kolam to base64
    buf_left = io.BytesIO()
    fig, ax = plt.subplots(figsize=(8,8))
    gray_img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
    ax.imshow(gray_img, cmap='gray')
    coords = np.column_stack(np.where(skeleton_left))
    ax.plot(coords[:,1], coords[:,0], '.', color='gray', markersize=1)
    for x, y in dots_left:
        ax.plot(x, y, 'ko', markersize=5)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(buf_left, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf_left.seek(0)
    analyzed_base64 = base64.b64encode(buf_left.read()).decode("utf-8")

    # 2️⃣ Right pane: analysis images from analyze_kolam_full_phone
    gray, edges, contours, skeleton, dots = analyze_kolam_full_phone(image_path)

    def to_base64(img_array, cmap=None, dots_overlay=None):
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(4,4))
        if cmap:
            ax.imshow(img_array, cmap=cmap)
        else:
            ax.imshow(img_array)
        if dots_overlay:
            for x, y in dots_overlay:
                ax.plot(x, y, 'ro', markersize=5)
        ax.axis('off')
        plt.tight_layout()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    dots_base64 = to_base64(gray, cmap='gray', dots_overlay=dots)
    contours_base64 = to_base64(contours, cmap='gray')
    edges_base64 = to_base64(edges, cmap='gray')
    skeleton_base64 = to_base64(skeleton, cmap='gray')

    return jsonify({
        "analyzed_kolam": analyzed_base64,  # left pane
        "dots": dots_base64,                # right gen1
        "contours": contours_base64,        # right gen2
        "edges": edges_base64,              # right gen3
        "skeleton": skeleton_base64         # right gen4
    })


@app.route("/styles")
def styles():
    return render_template("styles.html")


@app.route("/stylize", methods=["POST"])
def stylize():
    content_file = request.files.get("content")
    style_path = request.form.get("style")  # local path

    if not content_file or not style_path:
        return jsonify({"error": "Missing content or style"}), 400

    # Save uploaded image temporarily
    content_path = "temp_content.jpg"
    content_file.save(content_path)

    content = load_image(content_path, size=512).to(device)
    style = load_image(style_path, size=512).to(device)

    output = run_style_transfer(content, style, num_steps=200)
    output_img = tensor_to_pil(output)

    buf = io.BytesIO()
    output_img.save(buf, format="JPEG")
    buf.seek(0)

    return send_file(buf, mimetype="image/jpeg")

if __name__ == '__main__':
    app.run(debug=True)