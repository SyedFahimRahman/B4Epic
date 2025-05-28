from flask import Flask, redirect, url_for, render_template, session, flash, request
from extensions import db
import config
from allocation import run_allocation
from models import CompanyAssignment, Student, Company, User
from api import api_bp

# Flask-Admin imports
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

users = {}
pending_users = {}
admins = {"admin@admin.com": "admin"}

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = 'supersecretkey'

db.init_app(app)
app.register_blueprint(api_bp, url_prefix='/api')

# Flask-Admin setup
admin = Admin(app, name='Residency Admin', template_mode='bootstrap3')

# Custom admin view with access control
class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get("email") in admins

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access this page.")
        return redirect(url_for("login"))

# Register models with Flask-Admin
admin.add_view(AdminModelView(Student, db.session))
admin.add_view(AdminModelView(Company, db.session))
admin.add_view(AdminModelView(CompanyAssignment, db.session))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    if "username" in session:
        return f"Hello {session['username']}, welcome to the home page!"
    return redirect(url_for('login'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/log-in", methods=["GET", "POST"])
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

        # Check for company user
        company_user = User.query.filter_by(username=email, role="company").first()
        if company_user and company_user.password == password:
            if hasattr(company_user, "is_approved") and not company_user.is_approved:
                flash("Your account is pending admin approval.")
                return render_template("login.html")
            session["email"] = email
            session["role"] = "company"
            session["username"] = email
            session["company_id"] = company_user.id  # <-- This is important!
            return redirect(url_for("company.add_residency"))

        # Check for regular user (student, etc.)
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:
            if hasattr(user, "is_approved") and not user.is_approved:
                flash("Your account is pending admin approval.")
                return render_template("login.html")
            session["email"] = email
            session["role"] = user.role
            session["username"] = email
            return redirect(url_for("public.index"))

        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        company_name = request.form.get("company_name")
        num_of_positions = request.form.get("num_of_positions")
        # Optionally, get interview_required and address_id from the form

        if not email or not password or not confirm_password:
            flash("All fields are required.")
        elif password != confirm_password:
            flash("Passwords do not match.")
        elif User.query.filter_by(username=email).first():
            flash("Email already registered or pending approval.")
        else:
            if role == "company":
                # Create the company record
                company = Company(
                    name=company_name,
                    num_of_positions=num_of_positions,
                    interview_required=False  # or get from form if you want
                    # address_id=...  # if you collect address info
                )
                db.session.add(company)
                db.session.commit()
                # Create the user (optionally link to company if you add company_id to User)
                new_user = User(username=email, password=password, role="company", is_approved=False)
                db.session.add(new_user)
                db.session.commit()
                flash("Company account created! Waiting for admin approval.")
            else:
                user_role = role if role else "student"
                new_user = User(username=email, password=password, role=user_role, is_approved=False)
                db.session.add(new_user)
                db.session.commit()
                flash("Account created! Waiting for admin approval.")
            return redirect(url_for("auth.login"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("email", None)
    session.pop("role", None)
    session.pop("company_id", None)
    flash("Logged out successfully.")
    return redirect(url_for("public.index"))


@app.route("/contactus")
def contactus():
    return render_template("contactus.html")


@app.route("/admin-dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "email" not in session or session["email"] not in admins:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")
        user_email = request.form.get("user_email")

        if user_email in pending_users:
            if action == "approve":
                user_data = pending_users.pop(user_email)
                user_data["approved"] = True
                users[user_email] = user_data
                flash(f"Approved {user_email}")
            elif action == "reject":
                pending_users.pop(user_email)
                flash(f"Rejected {user_email}")

    return render_template("admin.html", pending_users=pending_users)


@app.route('/admin-dashboard/run-allocation')
def run_allocation_route():
    result = run_allocation(round_number=1)
    return result


@app.route('/view-assignments')
def view_assignments():
    assignments = CompanyAssignment.query.all()
    output = []
    for a in assignments:
        student = Student.query.get(a.student_id)
        company = Company.query.get(a.company_id)
        output.append(f"{student.first_name} {student.last_name} : {company.name}")
    return "<br>".join(output)


if __name__ == "__main__":
    app.run(debug=True)
