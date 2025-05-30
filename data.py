from app import app
from extensions import db
from models import User, Student, QCA, Company, ResidencyPosition, Preference
from datetime import datetime
import random

with app.app_context():
    db.create_all()
    
    """admin = User(
    username="admin@admin.com",
    password="admin",  # Use a hashed password in production!
    role="admin",
    is_approved=True
    )
    db.session.add(admin)
    db.session.commit()
    """

    # creating users
    user1 = User(username = "waleed.ahmad", password = "w1234", role = "student")
    user2 = User(username = "fahim.rahman", password = "f1234", role = "student")
    user3 = User(username="anna.maughan", password="a1234", role="student")
    user4 = User(username="yasmin.woodlock", password="y1234", role="student")
    user5 = User(username="daniel.tyutyunkov", password="d1234", role="student")
    user6 = User(username="eoin.okelly", password="e1234", role="student")
    user7 = User(username="peter.kennedy", password="p1234", role="student")
    user8 = User(username="ciaran.lynch", password="c1234", role="student")
    user9 = User(username="sebastian.kimmel", password="s1234", role="student")
    user10 = User(username="timothy.lazo", password="t1234", role="student")
    user11 = User(username="john.doe", password="j1234", role="company")
    user12 = User(username="jane.smith", password="j1234", role="company")
    user13 = User(username="company1", password="c1234", role="company")
    user14 = User(username="company2", password="c1234", role="company")
    
    db.session.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9, user10, user11, user12, user13, user14])
    db.session.flush() #to get IDs

    # creating students
    student1 = Student(id = user1.id, first_name = "Waleed", last_name = "Ahmad", phone_no = "123456")
    student2 = Student(id = user2.id, first_name = "Fahim", last_name = "Rahman", phone_no = "654321")
    student3 = Student(id=user3.id, first_name="Anna", last_name="Maughan", phone_no=None)
    student4 = Student(id=user4.id, first_name="Yasmin", last_name="Woodlock", phone_no=None)
    student5 = Student(id=user5.id, first_name="Daniel", last_name="Tyutyunkov", phone_no=None)
    student6 = Student(id=user6.id, first_name="Eoin", last_name="O'Kelly", phone_no=None)
    student7 = Student(id=user7.id, first_name="Peter", last_name="Kennedy", phone_no=None)
    student8 = Student(id=user8.id, first_name="Ciaran", last_name="Lynch", phone_no=None)
    student9 = Student(id=user9.id, first_name="Sebastian", last_name="Kimmel", phone_no=None)
    student10 = Student(id=user10.id, first_name="Timothy", last_name="Lazo", phone_no=None)
    db.session.add_all([student1, student2, student3, student4, student5, student6, student7, student8, student9, student10])
    db.session.commit()

    # qca scores
    # Add QCA scores for students
    qca_list = [
        QCA(student_id=student1.id, semester=1, qca_score=3.7),
        QCA(student_id=student2.id, semester=1, qca_score=3.9),
        QCA(student_id=student3.id, semester=1, qca_score=3.6),
        QCA(student_id=student4.id, semester=1, qca_score=3.5),
        QCA(student_id=student5.id, semester=1, qca_score=3.4),
        QCA(student_id=student6.id, semester=1, qca_score=3.3),
        QCA(student_id=student7.id, semester=1, qca_score=3.2),
        QCA(student_id=student8.id, semester=1, qca_score=3.1),
        QCA(student_id=student9.id, semester=1, qca_score=3.0),
        QCA(student_id=student10.id, semester=1, qca_score=2.9),
    ]
    db.session.add_all(qca_list)
    db.session.commit()

    # companies data
    companies = [
        Company(name="Google", num_of_positions=2),
        Company(name="Analog Devices", num_of_positions=3),
        Company(name="Stripe", num_of_positions=2),
        Company(name="Fidelity", num_of_positions=1),
        Company(name="Kneat", num_of_positions=1),
        Company(name="Provisio", num_of_positions=1),
        Company(name="Apple", num_of_positions=3),
        Company(name="CloudCards", num_of_positions=1),
        Company(name="Fiserv", num_of_positions=1),
        Company(name="Amazon", num_of_positions=3),
        Company(name="Intercom", num_of_positions=2),
        Company(name="DevEire", num_of_positions=1),
        Company(name="Johnson&Johnson", num_of_positions=2),
        Company(name="Dogpatch", num_of_positions=1),
        Company(name="Kirby", num_of_positions=1),
        Company(name="Patch", num_of_positions=1),
        Company(name="BD", num_of_positions=1),
        Company(name="Enterprise", num_of_positions=1),
        Company(name="Payslip", num_of_positions=1),
        Company(name="Shannonside Capital", num_of_positions=2),
    ]
    db.session.add_all(companies)
    db.session.commit()



    # Residency Positions
    # residency1 = ResidencyPosition(company_id = company1.id, year = datetime.now().year,
    #                                num_of_residencies = 2
    #                                )
    # residency2 = ResidencyPosition(company_id = company2.id, year = datetime.now().year,
    #                                num_of_residencies = 1
    #                                )
    # db.session.add_all([residency1, residency2])

   # preferences data
   # pref1 = Preference(student_id = student1.id, company_id = company1.id, preference_rank = 1)
   # pref2 = Preference(student_id = student1.id, company_id = company2.id, preference_rank = 2)
   # pref3 = Preference(student_id = student2.id, company_id = company2.id, preference_rank = 1)
   # pref4 = Preference(student_id = student2.id, company_id = company1.id, preference_rank = 2)
   # db.session.add_all([pref1, pref2, pref3, pref4])


    #creating residencies
    current_year = datetime.now().year
    residency_1 = Residency(year=current_year)
    residency_2 = Residency(year=current_year + 1)  # Next year residency

    db.session.add_all([residency_1, residency_2])
    db.session.commit()

    # create ResidencyPositions for all companies in both residencies
    for residency in [residency_1, residency_2]:
        for company in companies:
            rp = ResidencyPosition(
                residency_id=residency.id,
                company_id=company.id,
                num_of_residencies=company.num_of_positions,
                title = f"{company.name} Residency Position",
                is_combined = False
            )
            db.session.add(rp)
    db.session.commit()


#initial preference ranking
    all_students = [student1, student2, student3, student4, student5,
                    student6, student7, student8, student9, student10]


for student in all_students:
    shuffled_companies = companies[:]
    random.shuffle(shuffled_companies)
    for rank, company in enumerate(shuffled_companies, start=1):
        preference = Preference(
            student_id = student.id,
            company_id = company.id,
            preference_rank = rank
        )
        db.session.add(preference)

    db.session.commit()
    print("Data Inserted.")