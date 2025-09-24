from flask import Flask, render_template, request
import os
from model_utils import predict_image

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

results = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/results")
def results_page():
    return render_template("results.html", results=results)

@app.route("/models")
def models_page():
    return render_template("models.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    prediction = None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # 🔹 predikció a model_utils-ból
            prediction = predict_image(filepath)

            results.append({"filename": file.filename, "prediction": prediction})

    return render_template("upload.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
