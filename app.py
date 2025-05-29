from flask import Flask, redirect, url_for, render_template, session, flash, request
from extensions import db
import config
from allocation import run_allocation
from models import CompanyAssignment, Student, Company, ResidencyPosition, User

from api import api_bp

# Blueprints (optional modular organization)
from flask import Blueprint

# Initialize app
app = Flask(__name__)
app.config.from_object(config)
app.secret_key = 'supersecretkey'
db.init_app(app)

app.register_blueprint(api_bp, url_prefix='/api')

# ----------------- Public Routes -----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    if "email" in session:
        return f"Hello {session['email']}, welcome to the home page!"
    return redirect(url_for('login'))


# ----------------- Authentication -----------------
@app.route("/log-in", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter both email and password.")
            return render_template("login.html")

        user = User.query.filter_by(username=email).first()

        if user and user.password == password:
            if user.role == "admin":
                session["email"] = email
                session["role"] = "admin"
                return redirect(url_for("admin_panel"))
            elif user.role == "company":
                if not user.is_approved and user.role != "admin":
                    flash("Your account is pending admin approval.")
                    return render_template("login.html")
                session["email"] = email
                session["role"] = "company"
                session["company_id"] = user.id
                return redirect(url_for("index"))  # or another company dashboard if you have one
            else:
                if not user.is_approved:
                    flash("Your account is pending admin approval.")
                    return render_template("login.html")
                session["email"] = email
                session["role"] = user.role
                return redirect(url_for("index"))
        flash("Invalid credentials.")
    return render_template("login.html")


@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    is_first_user = User.query.count() == 0

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        company_name = request.form.get("company_name")
        num_of_positions = request.form.get("num_of_positions")

        if not email or not password or not confirm_password:
            flash("All fields are required.")
        elif password != confirm_password:
            flash("Passwords do not match.")
        elif User.query.filter_by(username=email).first():
            flash("Email already registered or pending approval.")
        else:
            # Automatically assign 'admin' to the first user
            if is_first_user:
                role = "admin"

            if role == "company":
                company = Company(name=company_name, num_of_positions=num_of_positions)
                db.session.add(company)
                db.session.commit()
                new_user = User(username=email, password=password, role="company", is_approved=False)
            else:
                new_user = User(username=email, password=password, role=role, is_approved=False)

            db.session.add(new_user)
            db.session.commit()
            if role == "admin":
                flash(f"{role.capitalize()} account created! You can log in now.")
            else:
                flash(f"{role.capitalize()} account created! Waiting for admin approval.")
            return redirect(url_for("login"))

    return render_template("signup.html", show_admin_option=is_first_user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("index"))

# ----------------- Admin Panel -----------------
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    user = User.query.filter_by(username=session.get("email")).first()
    if not user or user.role != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

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

    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template("admin.html", pending_users=pending_users)



#  creating route for allocation function of residency assignment
# ----------------- Allocation Routes -----------------
@app.route('/run-allocation')
def run_allocation_route():
    result = run_allocation(round_number=1)
    return result


# creating route for company assignments

@app.route('/view-assignments')
def view_assignments():
    assignments = CompanyAssignment.query.all()
    output = []
    for a in assignments:
        student = Student.query.get(a.student_id)
        company = Company.query.get(a.company_id)
        output.append(f"{student.first_name} {student.last_name} : {company.name}")
    return "<br>".join(output)

@app.route("/company/add-residency", methods=["GET", "POST"])
def add_residency():
    # Check if user is logged in and is an approved company
    if session.get("role") != "company":
        flash("Company access only.")
        return redirect(url_for("login"))
    user = User.query.get(session["company_id"])
    if not user or not user.is_approved:
        flash("Your account is pending admin approval.")
        return redirect(url_for("index"))

    # Get the company object (assuming one company per user)
    company = Company.query.filter_by(id=user.id).first()
    if not company:
        flash("No company profile found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        num_of_residencies = request.form.get("num_of_residencies")
        # Add more fields as needed

        new_position = ResidencyPosition(
            company_id=company.id,
            title=title,
            description=description,
            num_of_residencies=num_of_residencies
        )
        db.session.add(new_position)
        db.session.commit()
        flash("Residency position added!")
        return redirect(url_for("add_residency"))

    return render_template("add_residency.html")

if __name__ == "__main__":
    app.run(debug=True)
