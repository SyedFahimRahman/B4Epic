from app import app
from extensions import db
from app.models import User, Student, QCA, Company, RecidencyPosition, Preference, Round
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

    # creating users
    user1 = User(username = "waleed123", password = "1234", role = "student")
    user2 = User(username = "fahim123", password = "1234", role = "student")
    db.session.add_all([user1, user2])
    db.session.commit()

    # creating students
    student1 = Student(id = user1.id, first_name = "Waleed", last_name = "Ahmad", phone_no = "123456")
    student2 = Student(id = user2.id, first_name = "Fahim", last_name = "Rahman", phone_no = "654321")
    db.session.add_all([student1, student2])
    db.session.commit()

    # qca scores
    qca1 = QCA(student_id = student1.id, semester = 1, qca_score = 3.7)
    qca2 = QCA(student_id = student2.id, semester = 1, qca_score = 3.9)
    db.session.add_all([qca1, qca2])

    # companies data
    company1 = Company(name = "Google", num_of_positions = 2)
    company2 = Company(name = "Analog Devices", num_of_positions = 1)
    db.session.add_all([company1, company2])
    db.session.commit()

    # Residency Positions
    residency1 = RecidencyPosition(company_id = company1.id, year = datetime.now().year,
                                   num_of_residencies = 2
                                   )
    residency2 = RecidencyPosition(company_id = company2.id, year = datetime.now().year,
                                   num_of_residencies = 1
                                   )
    db.session.add_all([residency1, residency2])


    # preferences data
    pref1 = Preference(student_id = student1.id, company_id = company1.id, preference_rank = 1)
    pref2 = Preference(student_id = student1.id, company_id = company2.id, preference_rank = 2)
    pref3 = Preference(student_id = student2.id, company_id = company2.id, preference_rank = 1)
    pref4 = Preference(student_id = student2.id, company_id = company1.id, preference_rank = 2)
    db.session.add_all([pref1, pref2, pref3, pref4])

    db.session.commit()
    print("Data Inserted.")