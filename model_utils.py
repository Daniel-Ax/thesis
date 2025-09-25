import torch
from torchvision import transforms
from PIL import Image
import os
from model_def import SimpleCNN  # Saját CNN definíció

# --- Globális modell tároló ---
models = {}

def load_models():
    global models
    models = {
        "cnn": SimpleCNN(num_classes=3),
    }

    # CNN súlyok betöltése
    models["cnn"].load_state_dict(torch.load("models/cnn_best_model.pth", map_location="cpu"))
    models["cnn"].eval()

    # Dummy modellek – csak demonstráció
    models["vit"] = lambda x: "NORMAL"       # mindig NORMAL
    models["hybrid"] = lambda x: "COVID"     # mindig COVID
    models["ensemble"] = lambda x: "PNEUMONIA"  # mindig PNEUMONIA

load_models()

# --- Transzformáció ---
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

classes = ["COVID", "NORMAL", "PNEUMONIA"]

def predict_image(filepath, model_name="cnn"):
    if model_name not in models:
        raise ValueError(f"Ismeretlen modell: {model_name}")

    model = models[model_name]
    img = Image.open(filepath)
    img = transform(img).unsqueeze(0)

    if callable(model):  # dummy modellek
        return model(filepath)

    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)

    return classes[pred.item()]