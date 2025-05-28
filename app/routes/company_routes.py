import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import ResidencyPosition
from extensions import db
company_bp = Blueprint("company", __name__)

@company_bp.route("/add-residency", methods=["GET", "POST"])
def add_residency():
    if "role" not in session or session["role"] != "company":
        flash("Only company users can add residency.")
        return redirect(url_for("public.index"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        requirements = request.form.get("requirements")
        company_id = session.get("company_id")  # Set this when company logs in

        if not title or not description:
            flash("Title and description are required.")
        else:
            residency = ResidencyPosition(
                title=title,
                description=description,
                requirements=requirements,
                company_id=company_id
            )
            db.session.add(residency)
            db.session.commit()
            flash("Residency posted successfully!")
            return redirect(url_for("company.add_residency"))

    return render_template("add_residency.html")