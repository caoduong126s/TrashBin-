# 🌿 GreenSort - AI Waste Classification for Vietnam

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.15](https://img.shields.io/badge/tensorflow-2.15-orange.svg)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

AI-powered waste classification system optimized for Vietnamese waste types using Transfer Learning and EfficientNet.

## 📋 Features

- 🤖 **Deep Learning**: EfficientNetB0 with transfer learning
- 🇻🇳 **Vietnam-specific**: Fine-tuned on Vietnamese waste data
- 📊 **High Accuracy**: 88-92% on test set
- 🌐 **Web Demo**: Real-time classification via Streamlit
- 📱 **Mobile-ready**: Optimized for deployment
- 🔍 **Explainable AI**: Grad-CAM visualizations

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/waste-classification-vn.git
cd waste-classification-vn

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Download Data
```bash
# Download international dataset
python src/download_data.py

# Dataset will be saved to data/raw/
```

### Training
```bash
# Train baseline CNN
python src/train.py --model baseline

# Train EfficientNet (main model)
python src/train.py --model efficientnet

# Train with custom config
python src/train.py --config config.yaml
```

### Evaluation
```bash
# Evaluate on test set
python src/evaluate.py --model models/final/efficientnet_best.h5

# Generate reports
python src/evaluate.py --model models/final/efficientnet_best.h5 --report
```

### Demo
```bash
# Launch web demo
streamlit run demo/streamlit_app.py

# Open browser at http://localhost:8501
```

## 📊 Results

| Model | Accuracy | F1-Score | Params | Size |
|-------|----------|----------|--------|------|
| Baseline CNN | 72% | 0.70 | 2.3M | 9 MB |
| **EfficientNetB0** | **91%** | **0.90** | 5.3M | 29 MB |
| MobileNetV2 | 87% | 0.86 | 3.5M | 14 MB |
| ResNet50 | 89% | 0.88 | 25M | 98 MB |

## 📁 Project Structure
```
waste-classification-vn/
├── data/              # Datasets
├── notebooks/         # Jupyter notebooks
├── src/              # Source code
├── models/           # Saved models
├── outputs/          # Results
├── demo/             # Web demo
└── docs/             # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👏 Acknowledgments

- TrashNet dataset for initial training
- EfficientNet paper by Tan & Le (2019)
- Vietnam community for dataset contribution

