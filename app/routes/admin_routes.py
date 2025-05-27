from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import ResidencyPosition, User
from extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Check if the user is logged in and is an admin
    user = User.query.filter_by(username=session.get("email")).first()
    if not user or user.role != "admin":
        return redirect(url_for("auth.login"))

    # Handle approval/rejection of pending users
    if request.method == "POST":
        action = request.form.get("action")
        user_email = request.form.get("user_email")
        pending_user = User.query.filter_by(username=user_email, is_approved=False).first()

        if pending_user:
            if action == "approve":
                pending_user.is_approved = True
                db.session.commit()
                flash(f"Approved {user_email}")
            elif action == "reject":
                db.session.delete(pending_user)
                db.session.commit()
                flash(f"Rejected {user_email}")

    # Get all pending users
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template("admin.html", pending_users=pending_users)

@admin_bp.route('/upload-positions', methods=['GET', 'POST'])
def upload_positions():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            import csv
            stream = file.stream.read().decode("UTF8").splitlines()
            reader = csv.DictReader(stream)
            for row in reader:
                pos = ResidencyPosition(
                    company_id=row['company_id'],
                    year=row['year'],
                    num_of_residencies=row['num_of_residencies'],
                    is_combined=row.get('is_combined', False)
                )
                db.session.add(pos)
            db.session.commit()
            flash("Positions uploaded!")
            return redirect(url_for('admin.admin_panel'))
    return render_template('upload_positions.html')