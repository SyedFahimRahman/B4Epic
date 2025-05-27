from flask import Blueprint
from allocation import run_allocation
from app.models import CompanyAssignment, Student, Company

allocation_bp = Blueprint('allocation', __name__)

@allocation_bp.route('/run-allocation')
def run_allocation_route():
    result = run_allocation(round_number=1)
    return result

@allocation_bp.route('/view-assignments')
def view_assignments():
    assignments = CompanyAssignment.query.all()
    output = []
    for a in assignments:
        student = Student.query.get(a.student_id)
        company = Company.query.get(a.company_id)
        output.append(f"{student.first_name} {student.last_name} : {company.name}")
    return "<br>".join(output)