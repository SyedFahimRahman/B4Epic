from extensions import db
from models import Student, Preference, QCA, CompanyAssignment, RecidencyPosition, Round
from datetime import datetime

# function for allocation of students based on qca and preferences and company position availability
def run_allocation(round_number):

    round = Round.query.filter_by(round_number = round_number).first()
    if not round:
        round = Round(round_number = round_number)
        db.session.add(round)
        db.session.commit()


#     getting students with their most recent QCA scores
    students_qca = []
    for student in Student.query.all():
        latest_qca = QCA.query.filter_by(student_id = student.id).order_by(QCA.semester.desc()).first()
        if latest_qca:
            students_qca.append((student, latest_qca.qca_score))

#     Sorting students based on qca highest first order

    sorted_students = sorted(students_qca, key=lambda x: x[1], reverse=True)

#     Checking how many residencies are available per company

    positions = RecidencyPosition.query.filter_by(year = datetime.now().year).all()
    available_slots = {pos.company_id: pos.num_of_residencies for pos in positions}

    assigned_students = set(a.student_id for a in CompanyAssignment.query.all())

#     Go through each students and assigne based on preferences of the students
    for student, qca in sorted_students:
        if student.id in assigned_students:
            continue

        preferences = Preference.query.filter_by(student_id = student.id).order_by(Preference.preference_rank.asc()).all()
        for pref in preferences:
            if available_slots.get(pref.company_id, 0) > 0:
                assignment = CompanyAssignment(
                    student_id = student.id,
                    company_id = pref.company_id,
                    round_id = round.id
                )
                db.session.add(assignment)
                available_slots[pref.company_id] -= 1
                break  # break the loop when student is assigned to a company

    db.session.commit()
    return f"Allocation completed for round{round_number}"