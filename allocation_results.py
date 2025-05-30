from models import db, Student, Ranking, ResidencyPosition, CompanyAssignment
from sqlalchemy.orm import joinedload

def allocate_students():
    # Clear previous assignments
    CompanyAssignment.query.delete()
    db.session.commit()

    assigned_students = set()
    residency_slots = {}
    all_positions = ResidencyPosition.query.all()
    for pos in all_positions:
        residency_slots[pos.id] = {
            "total": pos.num_of_residencies,
            "assigned": 0
        }

    # Order students by grade ASC (lowest grade = highest priority)
    students = Student.query.order_by(Student.grade.asc()).all()
    for student in students:
        if student.id in assigned_students:
            continue

        # Use 'rank' field for ordering
        rankings = Ranking.query.filter_by(student_id=student.id).order_by(Ranking.rank.asc()).all()
        for rank in rankings:
            slot_info = residency_slots.get(rank.residency_id)
            if slot_info and slot_info["assigned"] < slot_info["total"]:
                res_pos = ResidencyPosition.query.get(rank.residency_id)
                assignment = CompanyAssignment(
                    student_id=student.id,
                    company_id=res_pos.company_id,
                    residency_id=res_pos.id,
                    title=res_pos.title,
                    round_id=1
                )
                db.session.add(assignment)
                slot_info["assigned"] += 1
                assigned_students.add(student.id)
                break

    db.session.commit()
    return f"Successfully assigned {len(assigned_students)} students."

def get_allocation_details():
    allocations = CompanyAssignment.query.options(
        joinedload(CompanyAssignment.residency).joinedload(ResidencyPosition.company),
        joinedload(CompanyAssignment.company)
    ).all()

    result = []
    for alloc in allocations:
        student = Student.query.get(alloc.student_id)
        residency = alloc.residency
        company = residency.company if residency else None

        result.append({
            'student_id': student.id if student else 'N/A',
            'student_name': f"{student.first_name} {student.last_name}" if student else 'N/A',
            'residency_id': residency.id if residency else 'N/A',
            'company_name': company.name if company else 'N/A',
            'job_title': residency.title if residency else 'N/A',
        })

    return result
