import torch
from torchvision import transforms
from PIL import Image
import os
from model_def import SimpleCNN  # Saját CNN definíció

# Példa: modellek betöltése
models = {}

def load_models():
    global models
    models = {
        "cnn": SimpleCNN(num_classes=3),
        # később: "vit": VisionTransformerModel(...),
        # később: "hybrid": HybridModel(...),
    }

    # Betöltjük a súlyokat
    models["cnn"].load_state_dict(torch.load("models/cnn_best_model.pth", map_location="cpu"))
    models["cnn"].eval()

    # Helyfoglalók (majd később ténylegesen betöltöd a ViT, Hybrid, Ensemble stb.)
    # models["vit"] = ...
    # models["hybrid"] = ...

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

    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)

    return classes[pred.item()]