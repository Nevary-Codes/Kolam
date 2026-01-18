# Kolam – Traditional Kolam Art Generation & Analysis
A deep-learning + computer-vision powered web application for generating, analyzing, and stylizing **South Indian Kolam designs**.

## 📌 Overview
Kolam is a complete pipeline for:
- Classification (Sikku / Pulli)
- Geometric & structural analysis
- Style transfer
- Web UI for uploads, generation, and learning Kolam principles

## 🚀 Features
### ✔ Kolam Classification
Detects Sikku or Pulli Kolam types.

### ✔ Kolam Analysis
- Dot detection
- Symmetry estimation
- Line tracing
- Pattern extraction

### ✔ Kolam Style Transfer
Apply artistic styles using neural networks.

### ✔ Web Interface
Pages:
- home.html
- design.html
- analysis.html
- styles.html
- principles.html

### ✔ Dataset
```
kolam_dataset/sikku/
kolam_dataset/pulli/
```

## 📁 Project Structure
```
Kolam/
│── app.py
│── main.py
│── main.ipynb
│── requirements.txt
│── pyproject.toml
│── kolam/
│   ├── kolam.py
│   ├── analysis.py
│   ├── style_transfer.py
│── templates/
│── static/
│   ├── css/
│   ├── js/
│   └── styles/
│── kolam_dataset/
│   ├── sikku/
│   └── pulli/
└── uploads/
```

## 🔧 Installation
```
git clone https://github.com/yourusername/kolam.git
cd kolam
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ▶ Running the App
```
python app.py
```
Visit: http://127.0.0.1:5000/

## 🧠 ML Components
- OpenCV-based analysis
- Geometry extraction
- PyTorch neural style transfer

## 📚 Future Improvements
- Deep learning classifier
- REST API
- Generative Kolam model
- Better dataset tools

## 📜 License
MIT (recommended)
