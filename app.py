from flask import Flask, render_template, request, redirect, url_for, session
import os
from model_utils import predict_image
from flask_dance.contrib.google import make_google_blueprint, google

# --- Flask alapbeállítások ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret")  # 🔐 Env változóból
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- Google OAuth blueprint ---
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # csak lokálban engedélyezett HTTP!
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# --- Google login/logout route-ok ---
@app.route("/login")
def login():
    return redirect(url_for("google.login"))

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    session["user"] = user_info
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# --- Saját route-ok ---
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