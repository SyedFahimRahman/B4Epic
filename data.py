from app import app
from extensions import db
from models import User, Student, QCA, Company, ResidencyPosition, Preference
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

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
    db.session.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9, user10])
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
    qca1 = QCA(student_id=student1.id, semester=1, qca_score=3.7)
    qca2 = QCA(student_id=student2.id, semester=1, qca_score=3.9)
    qca3 = QCA(student_id=student3.id, semester=1, qca_score=3.6)
    qca4 = QCA(student_id=student4.id, semester=1, qca_score=3.5)
    qca5 = QCA(student_id=student5.id, semester=1, qca_score=3.4)
    qca6 = QCA(student_id=student6.id, semester=1, qca_score=3.3)
    qca7 = QCA(student_id=student7.id, semester=1, qca_score=3.2)
    qca8 = QCA(student_id=student8.id, semester=1, qca_score=3.1)
    qca9 = QCA(student_id=student9.id, semester=1, qca_score=3.0)
    qca10 = QCA(student_id=student10.id, semester=1, qca_score=2.9)
    db.session.add_all([qca1, qca2, qca3, qca4, qca5,
        qca6, qca7, qca8, qca9, qca10])

    # companies data
    company1 = Company(name = "Google", num_of_positions = 2)
    company2 = Company(name = "Analog Devices", num_of_positions = 3)
    company3 = Company(name="Stripe", num_of_positions = 2)
    company4 = Company(name="Fidelity", num_of_positions = 1)
    company5 = Company(name="Kneat", num_of_positions= 1)
    company6 = Company(name="Provisio", num_of_positions= 1)
    company7 = Company(name="Apple", num_of_positions= 3)
    company8 = Company(name="CloudCards", num_of_positions= 1)
    company9 = Company(name="Fiserv", num_of_positions= 1)
    company10 = Company(name="Amazon", num_of_positions= 3)
    company11 = Company(name="Intercom", num_of_positions= 2)
    company12 = Company(name="DevEire", num_of_positions= 1)
    company13 = Company(name="Johnson&Johnson", num_of_positions=2)
    company14 = Company(name="Dogpatch", num_of_positions=1)
    company15 = Company(name="Kirby", num_of_positions= 1)
    company16 = Company(name="Patch", num_of_positions= 1)
    company17 = Company(name="BD", num_of_positions=1)
    company18 = Company(name="Enterprise", num_of_positions=1)
    company19 = Company(name="Payslip", num_of_positions=1)
    company20 = Company(name="Shannonside Capital", num_of_positions= 2)
    db.session.add_all([company1, company2, company3, company4, company5, company6, company7, company8, company9, company10,
        company11, company12, company13, company14, company15, company16, company17,
        company18, company19, company20])

    db.session.commit()

    # Residency Positions
    residency1 = ResidencyPosition(company_id = company1.id, year = datetime.now().year,
                                   num_of_residencies = 2
                                   )
    residency2 = ResidencyPosition(company_id = company2.id, year = datetime.now().year,
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