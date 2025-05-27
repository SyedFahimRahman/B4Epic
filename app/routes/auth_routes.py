from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User
from extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/log-in", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter both email and password.")
            return render_template("login.html")

        # Check for admin
        admin_user = User.query.filter_by(username=email, role="admin").first()
        if admin_user and admin_user.password == password:
            session["email"] = email
            session["role"] = "admin"
            session["username"] = email
            return redirect(url_for("admin.admin_panel"))

        # Check for regular user
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:
            # If you have an is_approved field, check it
            if hasattr(user, "is_approved") and not user.is_approved:
                flash("Your account is pending admin approval.")
                return render_template("login.html")
            session["email"] = email
            session["role"] = user.role
            session["username"] = email
            return redirect(url_for("public.index"))
        else:
            flash("Invalid credentials.")
    return render_template("login.html")

@auth_bp.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if not email or not password or not confirm_password or not role:
            flash("All fields are required.")
        elif password != confirm_password:
            flash("Passwords do not match.")
        elif User.query.filter_by(username=email).first():
            flash("Email already registered or pending approval.")
        else:
            # If you have an is_approved field, set it to False for non-admins
            is_approved = True if role == "admin" else False
            new_user = User(username=email, password=password, role=role)
            if hasattr(new_user, "is_approved"):
                new_user.is_approved = is_approved
            db.session.add(new_user)
            db.session.commit()
            if is_approved:
                flash("Account created! You can now log in.")
            else:
                flash("Account created! Waiting for admin approval.")
            return redirect(url_for("auth.login"))
    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("email", None)
    session.pop("role", None)
    flash("Logged out successfully.")
    return redirect(url_for("public.index"))