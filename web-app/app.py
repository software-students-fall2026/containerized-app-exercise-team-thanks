"""Flask web app for TACTILE."""

import os
import re
import pymongo
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, abort
from bson.objectid import ObjectId
from bson.errors import InvalidId
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError

load_dotenv()

connection = pymongo.MongoClient(os.getenv("MONGO_URI"))

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

db = connection[os.getenv("MONGO_DBNAME")]

users = db.users
users.create_index("email", unique=True)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(flask_login.UserMixin):
    """A logged in user, built from a document in the users collection."""

    def __init__(self, data):
        self.id = str(data["_id"])
        self.username = data["username"]
        self.email = data["email"]


@login_manager.user_loader
def load_user(user_id):
    """Look up the user stored in the session."""
    try:
        data = users.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        return None

    if data is None:
        return None

    return User(data)


@app.route("/")
def index():
    """Send visitors to the login page."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Show the login form and log the user in."""
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]

        data = db.users.find_one({"username": username})

        if data and check_password_hash(data["password_hash"], password):
            flask_login.login_user(User(data))
            return redirect(url_for("home"))

        return render_template("login.html", error="incorrect username or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Show the signup form and create a new user."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        if not username or not email or not password:
            return render_template("signup.html", error="missing fields")

        if len(password) < 8:
            return render_template(
                "signup.html", error="password must be 8 characters at least"
            )

        try:
            db.users.insert_one(
                {
                    "username": username.strip().lower(),
                    "email": email,
                    "password_hash": generate_password_hash(password),
                }
            )

            return redirect(url_for("login"))

        except DuplicateKeyError:
            return render_template("signup.html", error="user already exists")

    return render_template("signup.html")


@app.route("/home")
@flask_login.login_required
def home():
    """Show the logged-in user's sounds, newest first."""
    sounds = db.sounds.find({"user_id": flask_login.current_user.id}).sort(
        "created_at", -1
    )
    return render_template(
        "home.html", username=flask_login.current_user.username, sounds=list(sounds)
    )


@app.route("/sounds/<sound_id>")
@flask_login.login_required
def sound_detail(sound_id):
    """Show one of the logged-in user's sounds."""
    try:
        sound = db.sounds.find_one(
            {"_id": ObjectId(sound_id), "user_id": flask_login.current_user.id}
        )
    except InvalidId:
        abort(404)

    if sound is None:
        abort(404)

    return render_template("sound.html", sound=sound)


@app.route("/search")
@flask_login.login_required
def search():
    """Search the user's sounds by name or material, and filter by instrument."""
    user_id = flask_login.current_user.id
    text = request.args.get("q", "").strip()
    instrument = request.args.get("instrument", "")

    query = {"user_id": user_id}
    if text:
        pattern = {"$regex": re.escape(text), "$options": "i"}
        query["$or"] = [{"name": pattern}, {"material": pattern}]
    if instrument:
        query["instrument.type"] = instrument

    sounds = list(db.sounds.find(query).sort("created_at", -1))
    instruments = sorted(db.sounds.distinct("instrument.type", {"user_id": user_id}))

    return render_template(
        "search.html",
        sounds=sounds,
        text=text,
        instrument=instrument,
        instruments=instruments,
    )


@app.route("/logout")
@flask_login.login_required
def logout():
    """Log the user out."""
    flask_login.logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
