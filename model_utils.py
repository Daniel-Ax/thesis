import os
import torch
from torchvision import transforms
from PIL import Image
from model_def import SimpleCNN

# Modell betöltése
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn_best_model.pth")

model = SimpleCNN(num_classes=3)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# Transzformációk
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

classes = ["COVID", "NORMAL", "PNEUMONIA"]

def predict_image(filepath: str) -> str:
    img = Image.open(filepath)
    img = transform(img).unsqueeze(0)  # [1,1,224,224]
    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)
    return classes[pred.item()]