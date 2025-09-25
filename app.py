from flask import Flask, render_template, request, redirect, url_for, session
import os
from model_utils import predict_image
from flask_dance.contrib.google import make_google_blueprint, google
from functools import wraps
from dotenv import load_dotenv

# --- Környezeti változók betöltése ---
load_dotenv()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

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
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# --- Debug route-ok ---
@app.route("/_oauth_debug")
def oauth_debug():
    cb = url_for("google.authorized", _external=True)
    lg = url_for("google.login", _external=True)
    return {"callback_must_be_whitelisted": cb, "login_url": lg}

@app.route("/_client_debug")
def client_debug():
    return {
        "GOOGLE_CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET_SET": bool(os.environ.get("GOOGLE_CLIENT_SECRET")),
        "registered_redirect": url_for("google.authorized", _external=True),
    }

@app.route("/_user_debug")
def user_debug():
    return {"session_user": session.get("user")}

# --- Google login/logout route-ok ---
@app.route("/login")
def login():
    return redirect(url_for("google.login"))

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")

    if not resp or not resp.ok:
        return f"Google API hiba: {resp.text}", 500

    try:
        user_info = resp.json()
    except Exception as e:
        return f"Nem sikerült JSON-ná alakítani a választ: {resp.text} | Hiba: {e}", 500

    print("USER_INFO:", user_info)  # Debug konzolra

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
@login_required
def results_page():
    return render_template("results.html", results=results)

@app.route("/models")
def models_page():
    return render_template("models.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    prediction = None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            prediction = predict_image(filepath)
            results.append({"filename": file.filename, "prediction": prediction})

    return render_template("upload.html", prediction=prediction)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render adja a PORT-ot
    app.run(host="0.0.0.0", port=port)