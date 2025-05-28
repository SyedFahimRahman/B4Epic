from flask import Flask, redirect, url_for, render_template, session, flash, request
from extensions import db
import config
from allocation import run_allocation
from models import CompanyAssignment, Student, Company

# In-memory user stores (replace with DB for production)
users = {}
pending_users = {}
admins = {"admin@admin.com": "admin"}

app = Flask(__name__)
app.config.from_object(config)

app.secret_key = 'supersecretkey'

db.init_app(app)

# ===== Routes =====

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    # Use consistent session key 'email'
    if "email" in session:
        return f"Hello {session['email']}, welcome to the home page!"
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
            return redirect(url_for("admin"))

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
            # Add to pending users for admin approval
            pending_users[email] = {"password": password, "role": role, "approved": False}
            flash("Account created! Waiting for admin approval.")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("role", None)
    flash("Logged out successfully.")
    return redirect(url_for("index"))

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Protect admin route
    if "email" not in session or session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")   # 'approve' or 'reject'
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

@app.route('/run-allocation')
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
