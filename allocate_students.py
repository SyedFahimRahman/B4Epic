from models import db, Student, Ranking, ResidencyPosition, CompanyAssignment

def allocate_students():
    assigned_students = set()
    residency_slots = {}

    # Load available slots for each residency
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

        # Get this student's rankings, ordered by preference (lowest rank_score = top choice)
        rankings = Ranking.query.filter_by(student_id=student.id).order_by(Ranking.rank_score.asc()).all()

        for rank in rankings:
            slot_info = residency_slots.get(rank.residency_id)
            if slot_info and slot_info["assigned"] < slot_info["total"]:
                # Assign the student to this residency
                res_pos = ResidencyPosition.query.get(rank.residency_id)

                assignment = CompanyAssignment(
                    student_id=student.id,
                    company_id=res_pos.company_id,
                    residency_id=res_pos.id,
                    title=res_pos.title,
                    round_id=1  # or whatever round number is appropriate
                )
                db.session.add(assignment)

                slot_info["assigned"] += 1
                assigned_students.add(student.id)
                break  # Move to next student

    db.session.commit()
    return f"Successfully assigned {len(assigned_students)} students."
