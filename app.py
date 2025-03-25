from flask import Flask, request, jsonify, render_template
import torch
import timm
import torchvision.transforms as transforms
from PIL import Image

app = Flask(__name__)

# Load the trained ViT model
def load_model():
    model_path = "model.pth"
    model = timm.create_model("vit_large_patch16_224", pretrained=False, num_classes=4)
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

model = load_model()

# Define image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Class labels
class_names = ["CYST", "NORMAL", "STONE", "TUMOUR"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    img = Image.open(image).convert("RGB")
    img = transform(img).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = model(img)
        predicted_class = torch.argmax(output, dim=1).item()

    return jsonify({"prediction": class_names[predicted_class]})

if __name__ == "__main__":
    app.run(debug=True)
