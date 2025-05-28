from extensions import db
from models import Student, Preference, QCA, CompanyAssignment, ResidencyPosition, Round
from datetime import datetime

def run_allocation(round_number):

    current_round = Round.query.filter_by(round_number=round_number).first()
    if not current_round:
        current_round = Round(round_number=round_number)
        db.session.add(current_round)
        db.session.commit()

    students_qca = []
    for student in Student.query.all():
        latest_qca = QCA.query.filter_by(student_id=student.id).order_by(QCA.semester.desc()).first()
        if latest_qca:
            students_qca.append((student, latest_qca.qca_score))

    sorted_students = sorted(students_qca, key=lambda x: x[1], reverse=True)

    positions = ResidencyPosition.query.filter_by(year=datetime.now().year).all()
    available_slots = {pos.company_id: pos.num_of_residencies for pos in positions}

    assigned_students = set(a.student_id for a in CompanyAssignment.query.all())

    for student, qca in sorted_students:
        if student.id in assigned_students:
            continue

        preferences = Preference.query.filter_by(student_id=student.id).order_by(Preference.preference_rank.asc()).all()
        for pref in preferences:
            if available_slots.get(pref.company_id, 0) > 0:
                assignment = CompanyAssignment(
                    student_id=student.id,
                    company_id=pref.company_id,
                    round_id=current_round.id
                )
                db.session.add(assignment)
                available_slots[pref.company_id] -= 1
                break

    db.session.commit()
    return f"Allocation completed for round {round_number}"
