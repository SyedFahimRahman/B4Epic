from flask import Flask, redirect, url_for, render_template, session, flash, request
from extensions import db
import config
from allocation import run_allocation
from models import CompanyAssignment, Student, Company
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

        # Admin login
        if email in admins and admins[email] == password:
            session["email"] = email
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        # User login
        user = users.get(email)
        if user and user["password"] == password:
            if user["approved"]:
                session["email"] = email
                session["role"] = user["role"]
                return redirect(url_for("index"))
            else:
                flash("Your account is pending admin approval.")
        else:
            flash("Invalid credentials.")

    return render_template("login.html")


@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")  # 'company' or 'student'

        if not email or not password or not confirm_password or not role:
            flash("All fields are required.")
        elif password != confirm_password:
            flash("Passwords do not match.")
        elif email in users or email in pending_users:
            flash("Email already registered or pending approval.")
        else:
            pending_users[email] = {"password": password, "role": role, "approved": False}
            flash("Account created! Waiting for admin approval.")
            return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("email", None)
    flash("Logged out successfully.")
    return redirect(url_for("index"))


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
