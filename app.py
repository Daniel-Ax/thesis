from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # 🔹 Itt majd a modell előrejelzése fog futni
            prediction = "Predikció: Pneumonia (PLACEHOLDER)"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)