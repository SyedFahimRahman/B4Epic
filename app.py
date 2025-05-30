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
                if not user.is_approved:
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
                session["student_id"] = user.id
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
                year = request.form.get("year")

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
                    year=year,
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
        year = request.form.get("year")

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
            company_id=company.id,
            year = year
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

@app.route('/student/rank_residencies/<int:year>', methods=['GET', 'POST'])
@student_required
def rank_residencies(year):
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    if not student:
        flash("Student not found.")
        return redirect(url_for('index'))

    # Students can only rank residencies for their own year
    if student.year != year:
        flash("You cannot access another year's ranking page.")
        return redirect(url_for('index'))

    positions = ResidencyPosition.query.filter_by(year=year).all()

    if request.method == 'POST':
        position_order_str = request.form.get('position_order', '')
        if not position_order_str:
            flash("Please rank the positions before submitting.")
            return redirect(url_for('rank_residencies', year=year))

        position_ids = position_order_str.split(',')

        # Delete old rankings for this student
        Ranking.query.filter_by(student_id=student_id).delete()

        # Add new rankings
        for rank, pos_id in enumerate(position_ids, start=1):
            pos = ResidencyPosition.query.get(int(pos_id))
            if pos is None:
                continue
            ranking = Ranking(
                student_id=student_id,
                residency_id=pos.id,
                rank=rank
            )
            db.session.add(ranking)

        db.session.commit()
        flash("Your rankings have been saved!")
        return redirect(url_for('index'))

    return render_template('rank_residencies.html', positions=positions, year=year)

@app.route('/run-allocation/<int:year>', methods=["POST"])
def run_allocate_students(year):
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

    try:
        allocate_students(year=year)  # Pass year to your allocation function
        flash(f"Allocation complete for Year {year}.")
    except Exception as e:
        flash(f"Error during allocation: {str(e)}")
        return redirect(url_for("admin_panel"))  # Only on error

    # On success, redirect to results!
    return redirect(url_for("allocation_results", year=year))

@app.route("/allocation-results/<int:year>")
def allocation_results(year):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    allocations = [
        alloc for alloc in get_allocation_details()
        if Student.query.get(alloc['student_id']).year == year
    ]
    return render_template("allocation_result.html", allocations=allocations, year=year)
