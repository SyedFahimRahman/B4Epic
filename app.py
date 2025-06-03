# All the imports
from flask import Flask, render_template, session, request, redirect, url_for, flash
from functools import wraps
import csv
from io import TextIOWrapper
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from allocations import allocate_students, get_allocation_details, notify_allocation
from sqlalchemy import func
from flask_mail import Mail
from dotenv import load_dotenv


# Initialize app
load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy() # for database management
mail = Mail()  # mail initialization
from models import *

app.secret_key = 'supersecretkey'
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)



# Decorator to make student-only pages
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            flash("You must be logged in as a student to see this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# General ROutes
@app.route("/")
def index():

    student = None
    if session.get("role") == "student" and session.get("student_id"):
        from models import Student
        student = Student.query.get(session["student_id"])
    return render_template("index.html", student=student)
# Authentication
@app.route("/log-in", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter both email and password.")
            return render_template("login.html")

        user = User.query.filter_by(username=email).first()

    #Check credentials and role
        if user and check_password_hash(user.password, password):
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

            else:
                # Check approval
                if not user.is_approved:
                    flash("Your account is pending admin approval.")
                    return render_template("login.html")

                session["email"] = email
                session["role"] = user.role
                session["student_id"] = user.id
                return redirect(url_for("index"))
        flash("Invalid credentials.")
    return render_template("login.html")

# Sign-up page for new users
@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    #Sign-up page if first user ever to assign admin role
    is_first_user = User.query.count() == 0

    if request.method == "POST":
        # Get all form data
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        company_name = request.form.get("company_name")

        # Validate
        if not email or not password or not confirm_password:
            flash("All fields are required.")
        elif password != confirm_password:
            flash("Passwords do not match.")
        elif User.query.filter_by(username=email).first():
            flash("Email already registered or pending approval.")
        else:
            # Automatically assign admin to the first user
            if is_first_user:
                role = "admin"

            if role == "company":
                # Company registration
                line_1 = request.form.get("line_1")
                line_2 = request.form.get("line_2")
                town = request.form.get("town")
                county = request.form.get("county")
                eircode = request.form.get("eircode")

                # Create address
                address = Address(
                    line_1=line_1,
                    line_2=line_2,
                    town=town,
                    county=county,
                    eircode=eircode
                )
                db.session.add(address)
                db.session.flush()
                company = Company(name=company_name, address_id = address.id) # get address.id before commit
                db.session.add(company)
                db.session.flush()

                # hashing the password before saving it
                hashed_password = generate_password_hash(password)

                # Create user and associate with company
                new_user = User(
                    username=email,
                    password=hashed_password,
                    role="company",
                    is_approved=False,
                    company_id=company.id
                )
                db.session.add(new_user)
                db.session.commit()

            elif role == "student":
                # Student registration
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                phone_no = request.form.get("phone_no")
                year =  request.form.get("year")

                # hashing the password before saving it
                hashed_password = generate_password_hash(password)

                # Create user record
                new_user = User(
                    username=email,
                    password=hashed_password,
                    role="student",
                    is_approved=False
                )
                db.session.add(new_user)
                db.session.commit()

                # Create student record and associate with user
                new_student = Student(
                    id=new_user.id,
                    first_name=first_name,
                    last_name=last_name,
                    phone_no=phone_no,
                    year=year,
                    address_id=None
                )
                db.session.add(new_student)
                db.session.commit()

            else:
                # default for other roles
                hashed_password = generate_password_hash(password)
                new_user = User(
                    username=email,
                    password=hashed_password,
                    role=role,
                    is_approved=False
                )
                db.session.add(new_user)
                db.session.commit()

            flash(f"{role.capitalize()} account created! Waiting for admin approval.")
            return redirect(url_for("login"))

    return render_template("signup.html", show_admin_option=is_first_user)

# Logout that clears session and returns to home
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("index"))

#  Admin Panel
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Check if user is admin first
    user = User.query.filter_by(username=session.get("email")).first()
    if not user or user.role != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

    if request.method == "POST":
        # handle user or position approval
        action = request.form.get("action")
        user_email = request.form.get("user_email")
        position_id = request.form.get("position_id")

        if user_email:  # User approval logic
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

        elif position_id:  # Residency position approval logic
            position = ResidencyPosition.query.get(int(position_id))
            if position:
                if action == "approve":
                    position.is_approved = True
                    db.session.commit()
                    flash(f"Approved position '{position.title}' from {position.company.name}")
                elif action == "reject":
                    db.session.delete(position)
                    db.session.commit()
                    flash(f"Rejected position '{position.title}'")

    # Get all data for the admin panel
    pending_users = User.query.filter_by(is_approved=False).all()
    pending_positions = ResidencyPosition.query.filter_by(is_approved=False).all()

    # Try to get students with their associated user data using join
    # This is useful for displaying both student profile info and their user login info together
    try:
        # The join is on Student.id == User.id (since each student is also a user)
        students_with_users = db.session.query(Student, User).join(User, Student.id == User.id).all()
    except Exception as e:
        print(f"Error joining students with users: {e}")
        students_with_users = None

    # Fallback: get students separately if join fails
    students = Student.query.all()
    companies = Company.query.all()

    # Render the admin panel template, passing the data to the template
    return render_template(
        "admin.html",
        pending_users=pending_users,
        pending_positions=pending_positions,
        students_with_users=students_with_users,  # Pass the joined data (might be None)
        students=students,  # Fallback data
        companies=companies,
        User=User
    )
# For companies to upload residencies
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

        try:
            num_of_residencies = int(request.form.get("num_of_residencies"))
            if num_of_residencies < 1:
                raise ValueError("Number of residencies must be at least 1.")
        except (TypeError, ValueError):
            flash("Please enter a valid number for residencies.")
            return redirect(url_for("add_residency"))

        try:
            salary = float(request.form.get("salary"))
            if salary < 0:
                raise ValueError("Salary cannot be negative.")
        except (TypeError, ValueError):
            flash("Please enter a valid number for salary.")
            return redirect(url_for("add_residency"))

        workplace_type = request.form.get("workplace_type")
        if workplace_type not in ["on-site", "remote", "hybrid"]:
            flash("Please select a valid workplace type (remote, hybrid, onsite).")
            return redirect(url_for("add_residency"))

        accommodation_support = request.form.get("accommodation_support") == "yes"
        residency_type = request.form.get("residency_type")
        year = int(request.form.get("year"))
        company.contact = request.form.get("contact")

        # Address fields from form
        line_1 = request.form.get("line_1")
        line_2 = request.form.get("line_2")
        town = request.form.get("town")
        county = request.form.get("county")
        eircode = request.form.get("eircode")

        # Update or create company address
        if company.address_id:
            address = Address.query.get(company.address_id)
            address.line_1 = line_1
            address.line_2 = line_2
            address.town = town
            address.county = county
            address.eircode = eircode
        else:
            address = Address(
                line_1=line_1,
                line_2=line_2,
                town=town,
                county=county,
                eircode=eircode
            )
            db.session.add(address)
            db.session.flush()
            company.address_id = address.id

        # Create and save the new residency position
        new_position = ResidencyPosition(
            title=title,
            description=description,
            num_of_residencies=num_of_residencies,
            residency=residency_type,
            salary=salary,
            workplace_type=workplace_type,
            accommodation_support=accommodation_support,
            company_id=company.id,
            year=year,
            is_approved=False
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
        address=address,
        company_username=user.username
    )

# Show all the residencies
@app.route("/residencies")
def list_residencies():
    student = None
    if session.get("role") == "student" and session.get("student_id"):
        student = Student.query.get(session["student_id"])
        # Remove any incomplete or extra lines like "student = " here!

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
            "salary": f"${position.salary:,}" if position.salary else "Not specified",
            "accommodation_support": "Yes" if position.accommodation_support else "No",
            "company_name": company.name,
            "workplace_type": position.workplace_type,
            "contact": company.contact,
            "address_line_1": address.line_1,
            "address_line_2": address.line_2,
            "town": address.town,
            "county": address.county,
            "eircode": address.eircode,
        })

    return render_template("residency_list.html", residencies=residencies_data, student=student)

# For students to rank the residencies
@app.route('/student/rank_residencies/<int:year>', methods=['GET', 'POST'])
@student_required
def rank_residencies(year):
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    if not student:
        flash("Student not found.")
        return redirect(url_for('index'))

    # Prevent students from accessing other years' ranking pages
    if student.year != year:
        flash("You cannot access another year's ranking page.")
        return redirect(url_for('index'))

    # Only show positions for the student's year
    positions = ResidencyPosition.query.filter_by(year=student.year).all()

    if request.method == 'POST':
        # Get the order of positions from the form
        position_order_str = request.form.get('position_order', '')
        if not position_order_str:
            flash("Please rank the positions before submitting.")
            return redirect(url_for('rank_residencies', year=year))

        position_ids = position_order_str.split(',')

        # Delete old rankings for this student
        Ranking.query.filter_by(student_id=student_id).delete()

        # Add new rankings based on the submitted order
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

    # Render the template with the correct positions and student
    return render_template('rank_residencies.html', positions=positions, student=student)

@app.route('/student/view_rankings')
@student_required
def view_rankings():
    student_id = session.get('student_id')
    # Join Ranking with ResidencyPosition and Company for display
    rankings = (
        db.session.query(Ranking, ResidencyPosition, Company)
        .join(ResidencyPosition, Ranking.residency_id == ResidencyPosition.id)
        .join(Company, ResidencyPosition.company_id == Company.id)
        .filter(Ranking.student_id == student_id)
        .order_by(Ranking.rank)
        .all()
    )
    return render_template('view_rankings.html', rankings=rankings)


@app.route('/upload-students', methods=['POST'])
def upload_students():
    year = request.form.get('year', type=int)
    if not year:
        flash("Year is required.")
        return redirect(url_for('admin_panel'))

    file = request.files.get('file')
    if not file or file.filename == '':
        flash("No file selected.")
        return redirect(url_for('admin_panel'))

    if not file.filename.lower().endswith('.csv'):
        flash("Only CSV files are allowed.")
        return redirect(url_for('admin_panel'))

    try:
        # Read the CSV file
        csv_file = TextIOWrapper(file.stream, encoding='utf-8-sig')
        reader = csv.DictReader(csv_file)

        # Debug: Print headers
        print("CSV Headers:", reader.fieldnames)

        # Track updates and creations
        updated_count = 0
        created_count = 0
        error_count = 0

        for row in reader:
            try:
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                grade_str = row.get('grade', '').strip()
                email = row.get('email', '').strip()
                if not email:
                    print(f"Row {reader.line_num}: Missing email. Skipped.")
                    error_count += 1
                    continue

                # Debug: Print current row data
                print(f"Processing row {reader.line_num}: {first_name} {last_name}, grade: '{grade_str}'")

                if not first_name or not last_name:
                    print(f"Row {reader.line_num}: Missing first or last name. Skipped.")
                    error_count += 1
                    continue

                # Handle grade conversion more carefully
                grade = None
                if grade_str:
                    try:
                        grade = float(grade_str)  # Use float to handle decimal grades
                        if grade < 0 or grade > 100:
                            print(f"Row {reader.line_num}: Grade {grade} out of range. Skipped.")
                            error_count += 1
                            continue
                    except ValueError:
                        print(f"Row {reader.line_num}: Invalid grade '{grade_str}'. Skipped.")
                        error_count += 1
                        continue

                # Find existing student - FIXED QUERY
                student = db.session.query(Student).join(User, Student.id == User.id).filter(
                    func.lower(Student.first_name) == func.lower(first_name),
                    func.lower(Student.last_name) == func.lower(last_name),
                    Student.year == year
                ).first()

                if student:
                    # Update existing student
                    print(f"Found existing student: {student.first_name} {student.last_name}")
                    print(f"Current grade: {student.grade}, New grade: {grade}")

                    # Update grade if provided
                    if grade is not None:
                        student.grade = grade
                        print(f"Updated grade to: {student.grade}")

                    # Update email if provided in CSV and different
                    if row.get('email') and row.get('email').strip():
                        user = User.query.get(student.id)
                        if user and user.username != email:
                            user.username = email
                            print(f"Updated email to: {email}")

                    updated_count += 1
                else:
                    print(f"Row {reader.line_num}: Student {first_name} {last_name} (year {year}) not found. Skipped.")
                    error_count += 1
                    continue

            except Exception as row_error:
                print(f"Error processing row {reader.line_num}: {str(row_error)}")
                error_count += 1
                continue

        # Commit all changes
        db.session.commit()
        print(f"Database committed successfully")

        flash(
            f"Upload complete for Year {year}. Updated: {updated_count}, Created: {created_count}, Errors: {error_count}")

    except Exception as e:
        db.session.rollback()
        print(f"Database rolled back due to error: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        app.logger.error(f"Error in upload_students: {str(e)}", exc_info=True)

    return redirect(url_for('admin_panel'))
@app.route('/run-allocation', methods=["POST"])
def run_allocate_students():
    year = request.form.get("year", type=int)
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("login"))

    try:
        print(allocate_students)
        CompanyAssignment.query.filter_by(round_id=1).delete()
        db.session.commit() #clear all like matching

        allocate_students(year)
        notify_allocation(year)
        flash(f"Allocation completed and emails sent for Year {year}.")
        return redirect(url_for("allocation_results", year=year))
    except Exception as e:
        flash(f"Error during allocation: {str(e)}")
        return redirect(url_for("admin_panel"))

@app.route("/allocation-results")
def allocation_results():
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        allocations = get_allocation_details()
        return render_template("allocation_results.html", allocations=allocations)


if __name__ == '__main__':
    app.run(debug=True)
