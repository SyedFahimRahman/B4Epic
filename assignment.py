from models import CompanyAssignment, ResidencyPosition
from sqlalchemy.orm import joinedload

def get_allocation_details():
    allocations = CompanyAssignment.query.options(
        joinedload(CompanyAssignment.student),
        joinedload(CompanyAssignment.residency).joinedload(ResidencyPosition.company),
        joinedload(CompanyAssignment.company)
    ).all()

    result = []
    for alloc in allocations:
        student = alloc.student
        residency = alloc.residency
        company = residency.company if residency else None

        result.append({
            'student_id': student.id if student else 'N/A',
            'residency_id': residency.id if residency else 'N/A',
            'company_name': company.name if company else 'N/A',
            'job_title': residency.title if residency else 'N/A',
        })

    return result
