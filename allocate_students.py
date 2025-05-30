from models import db, Student, Ranking, ResidencyPosition, CompanyAssignment
from sqlalchemy.orm import joinedload

def allocate_students():
    assigned_students = set()
    residency_slots = {}

    # Load how many students can be placed in each residency
    all_positions = ResidencyPosition.query.all()
    for pos in all_positions:
        residency_slots[pos.id] = {
            "total": pos.num_of_residencies,
            "assigned": 0
        }

    # Order students by grade ASC (lowest grade = higher priority)
    students = Student.query.order_by(Student.grade.asc()).all()
    for student in students:
        if student.id in assigned_students:
            continue

        rankings = Ranking.query.filter_by(student_id=student.id).order_by(Ranking.rank_score.asc()).all()

        for rank in rankings:
            slot_info = residency_slots.get(rank.residency_id)

            if slot_info and slot_info["assigned"] < slot_info["total"]:
                # <-- Put the prints here, just before assignment creation:
                print(f"Assigning Student {student.id} to Residency {rank.residency_id}, Company {rank.company_id}")
                res_pos = ResidencyPosition.query.get(rank.residency_id)
                print(f"Residency Position: {res_pos}, Title: {res_pos.title if res_pos else 'None'}")

                # Now create and add assignment
                assignment = CompanyAssignment(
                    student_id=student.id,
                    company_id=rank.company_id,
                    residency_id=rank.residency_id,
                    title=res_pos.title if res_pos else None,
                    round_id=None
                )
                db.session.add(assignment)

                slot_info["assigned"] += 1
                assigned_students.add(student.id)
                break


    db.session.commit()
    return f"Successfully assigned {len(assigned_students)} students."
