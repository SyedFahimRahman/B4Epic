from extensions import db
from models import Student, Preference, QCA, CompanyAssignment, ResidencyPosition, Interview, Round
from datetime import datetime
import random

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

    positions = ResidencyPosition.query.all()
    available_slots = {pos.company_id: pos.num_of_residencies for pos in positions}

    assigned_students = set(a.student_id for a in CompanyAssignment.query.all())

#     Go through each student and assign based on preferences of the students
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
    return f"Allocation completed for round {round_number}"


def run_initial_interview_matching(round_number):
    # Making sure the round exists
    round = Round.query.filter_by(round_number=round_number).first()
    if not round:
        round = Round(round_number=round_number)
        db.session.add(round)
        db.session.commit()

     # Get all students
    students = Student.query.all()

    # Get list of available companies for this year
    available_positions = ResidencyPosition.query.all()
    all_company_ids = [pos.company_id for pos in available_positions]

    # Loop through each student
    for student in students:
        # Get student's ranked preferences
        preferences = Preference.query.filter_by(student_id=student.id).order_by(
        Preference.preference_rank).all()
        preferred_ids = [pref.company_id for pref in preferences]

        # Take top 3 preferences, or fewer if not enough
        selected_ids = preferred_ids[:3]

        # If fewer than 3 preferences, randomly pick others from remaining companies
        remaining_needed = 3 - len(selected_ids)
        if remaining_needed > 0:
            remaining_ids = list(set(all_company_ids) - set(selected_ids))
            random.shuffle(remaining_ids)
            selected_ids += remaining_ids[:remaining_needed]

        # Create interview assignments
        for company_id in selected_ids:
            interview = Interview(
                student_id=student.id,
                company_id=company_id,
                round_id=round.id
            )
            db.session.add(interview)


    db.session.commit()
    return f"Allocation completed for round{round_number}"
