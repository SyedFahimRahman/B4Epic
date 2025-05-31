import app
from flask import Flask, redirect, url_for, render_template, session, flash, request
from functools import wraps

from allocation_results import get_allocation_details

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from allocation_results import allocate_students, get_allocation_details
from api import api_bp
from models import *


# Blueprints (optional modular organization)
from flask import Blueprint

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
from models import *

app.secret_key = 'supersecretkey'
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_bp, url_prefix='/api')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            flash("You must be logged in as a student to see this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- Public Routes -----------------
from flask import session, render_template

@app.route("/")
def index():
    student = None
    if session.get("role") == "student" and session.get("student"):
        student = session.get("student")
    return render_template("index.html", student=student)


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
                if not user.is_approved:
                    flash("Your account is pending admin approval.")
                    return render_template("login.html")
                session["email"] = email
                session["role"] = "company"
                session["company_id"] = user.id
                return redirect(url_for("index"))

            elif user.role == "student":
                if not user.is_approved:
                    flash("Your account is pending admin approval.")
                    return render_template("login.html")
                session["email"] = email
                session["role"] = "student"
                session["student_id"] = user.id

                # Fetch the student record
                student_obj = Student.query.get(user.id)
                if student_obj:
                    session["student"] = {
                        "id": student_obj.id,
                        "year": student_obj.year if hasattr(student_obj, 'year') else 2025,
                        "first_name": student_obj.first_name,
                        "last_name": student_obj.last_name
                    }
                else:
                    # fallback if student not found
                    session["student"] = {
                        "id": user.id,
                        "year": 2025,
                        "first_name": "",
                        "last_name": ""
                    }

                return redirect(url_for("index"))

            else:
                # Other roles
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

            new_user = None

            if role == "company":
                company = Company(name=company_name)
                db.session.add(company)
                db.session.commit()

                new_user = User(
                    username=email,
                    password=password,
                    role="company",
                    is_approved=False,
                    company_id=company.id
                )
                db.session.add(new_user)
                db.session.commit()

            elif role == "student":
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                phone_no = request.form.get("phone_no")

                new_user = User(
                    username=email,
                    password=password,
                    role="student",
                    is_approved=False
                )
                db.session.add(new_user)
                db.session.commit()

                new_student = Student(
                    id=new_user.id,
                    first_name=first_name,
                    last_name=last_name,
                    phone_no=phone_no,
                    address_id=None  # You can modify this if you collect address info
                )
                db.session.add(new_student)
                db.session.commit()

            else:
                new_user = User(
                    username=email,
                    password=password,
                    role=role,
                    is_approved=False
                )
                db.session.add(new_user)
                db.session.commit()

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
        item_type = request.form.get("item_type")

        if item_type == "user":
            user_email = request.form.get("user_email")
            pending_user = User.query.filter_by(username=user_email, is_approved=False).first()

            if pending_user:
                if action == "approve":
                    pending_user.is_approved = True
                    db.session.commit()
                    flash(f"Approved user: {user_email}")
                elif action == "reject":
                    db.session.delete(pending_user)
                    db.session.commit()
                    flash(f"Rejected user: {user_email}")

        elif item_type == "residency":
            position_id = request.form.get("position_id")
            position = ResidencyPosition.query.get(position_id)

            if position and not position.is_approved:
                if action == "approve":
                    position.is_approved = True
                    db.session.commit()
                    flash(f"Approved residency: {position.title}")
                elif action == "reject":
                    db.session.delete(position)
                    db.session.commit()
                    flash(f"Rejected residency: {position.title}")

    pending_users = User.query.filter_by(is_approved=False).all()
    pending_positions = ResidencyPosition.query.filter_by(is_approved=False).all()

    return render_template("admin.html", pending_users=pending_users, pending_positions=pending_positions)


# ----------------- Allocation Routes -----------------
"""@app.route('/run-allocation')
def run_allocation_route():
    result = run_allocation(round_number=1)
    return result
"""

# ----------------- Company Assignments -----------------
@app.route('/view-assignments')
def view_assignments():
    assignments = CompanyAssignment.query.all()
    output = []
    for a in assignments:
        student = Student.query.get(a.student_id)
        company = Company.query.get(a.company_id)
        output.append(f"{student.first_name} {student.last_name} : {company.name}")
    return "<br>".join(output)

@app.route("/company/add_residency", methods=["GET", "POST"])
def add_residency():
    # Check if user is logged in and is an approved company
    if session.get("role") != "company":
        flash("Company access only.")
        return redirect(url_for("login"))

    user = User.query.get(session["company_id"])
    if not user or not user.is_approved:
        flash("Your account is pending admin approval.")
        return redirect(url_for("index"))

    company = Company.query.get(user.company_id)
    if not company:
        flash("Associated company not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Residency position fields
        title = request.form.get("title")
        description = request.form.get("description")
        num_of_residencies = request.form.get("num_of_residencies")
        residency_type = request.form.get("residency_type")  # dropdown value
        is_combined_str = request.form.get("is_combined")  # "true" or "false"

        is_combined = True if is_combined_str == "true" else False

        # Address fields from form
        line_1 = request.form.get("line_1")
        line_2 = request.form.get("line_2")
        town = request.form.get("town")
        county = request.form.get("county")
        eircode = request.form.get("eircode")

        # Update or create company address
        if company.address_id:
            # Existing address - update it
            address = Address.query.get(company.address_id)
            address.line_1 = line_1
            address.line_2 = line_2
            address.town = town
            address.county = county
            address.eircode = eircode
        else:
            # No address yet - create one
            address = Address(
                line_1=line_1,
                line_2=line_2,
                town=town,
                county=county,
                eircode=eircode
            )
            db.session.add(address)
            db.session.flush()  # flush to get the address id before commit
            company.address_id = address.id

        # Add the new residency position
        new_position = ResidencyPosition(
            title=title,
            description=description,
            num_of_residencies=num_of_residencies,
            residency=residency_type,
            is_combined=is_combined,
            company_id=company.id
        )

        db.session.add(new_position)
        db.session.commit()

        flash("Residency position and company address updated!")
        return redirect(url_for("add_residency"))

    # For GET request, pass current address data to template for pre-filling
    address = None
    if company.address_id:
        address = Address.query.get(company.address_id)

    return render_template(
        "add_residency.html",
        company_name=company.name,
        address=address
    )

@app.route("/residencies")
def list_residencies():
    # Query all ResidencyPositions with their related Company and Address data
    positions = db.session.query(
        ResidencyPosition,
        Company,
        Address
    ).join(Company, ResidencyPosition.company_id == Company.id
    ).join(Address, Company.address_id == Address.id
    ).all()

    # Prepare a list of dicts to send to template
    residencies_data = []
    for position, company, address in positions:
        residencies_data.append({
            "title": position.title,
            "description": position.description,
            "num_of_residencies": position.num_of_residencies,
            "residency_type": position.residency,
            "is_combined": position.is_combined,
            "company_name": company.name,
            "contact": company.contact,
            "address_line_1": address.line_1,
            "address_line_2": address.line_2,
            "town": address.town,
            "county": address.county,
            "eircode": address.eircode,
        })

    return render_template("residency_list.html", residencies=residencies_data)


@app.route("/student/rank_residencies", methods=["GET", "POST"])
def rank_residencies():
    student = session.get("student")
    if not student:
        flash("You need to log in as a student to access this page.")
        return redirect(url_for("login"))

    positions = (
        db.session.query(ResidencyPosition, Company)
        .join(Company, ResidencyPosition.company_id == Company.id)
        .filter(ResidencyPosition.is_approved == True)  # Optional: only approved ones
        .all()
    )

    # Format data to pass to template
    positions_list = []
    for position, company in positions:
        positions_list.append({
            "id": position.id,
            "company_id": company.name,  # Or company.id if you prefer
            "title": position.title,
            "num_of_residencies": position.num_of_residencies
        })

    if request.method == "POST":
        position_order = request.form.get("position_order")
        if position_order:
            flash("Your residency rankings have been saved!")
            return redirect(url_for("rank_residencies"))

    # Fix the year to 2025 here explicitly:
    student['year'] = 2025

    return render_template("rank_residencies.html", positions=positions_list, student=student)

@app.route('/run-allocation', methods=["POST"])
def run_allocate_students():
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

    try:
        allocate_students()
        flash("Allocation complete.")
    except Exception as e:
        flash(f"Error during allocation: {str(e)}")
        return redirect(url_for("admin_panel"))  # Only on error

    # On success, redirect to results!
    return redirect(url_for("allocation_results"))

@app.route("/allocation-results")
def allocation_results():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    allocations = get_allocation_details()
    return render_template("allocation_results.html", allocations=allocations)
