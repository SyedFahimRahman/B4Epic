from flask import Blueprint, render_template, session, redirect, url_for

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def index():
    return render_template("index.html")

@public_bp.route("/home")
def home():
    if "username" in session:
        return f"Hello {session['username']}, welcome to the home page!"
    return redirect(url_for("auth.login"))

@public_bp.route("/contactus")
def contactus():
    return render_template("contactus.html")
