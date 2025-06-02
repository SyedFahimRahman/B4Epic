from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    is_approved = db.Column(db.Boolean, default=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)

    company = db.relationship('Company', backref='users', lazy=True)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line_1 = db.Column(db.String(100))
    line_2 = db.Column(db.String(100))
    town = db.Column(db.String(50))
    county = db.Column(db.String(50))
    eircode = db.Column(db.String(10))


class Student(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_no = db.Column(db.String(20))
    grade = db.Column(db.Integer)
    year = db.Column(db.Integer)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', backref='students', lazy=True)


class QCA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    semester = db.Column(db.Integer)
    qca_score = db.Column(db.Float)


class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True)
    file_path = db.Column(db.String(255))


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', backref='companies', lazy=True)
    num_of_positions = db.Column(db.Integer, nullable=False, default=0)

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    preference_rank = db.Column(db.Integer)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, unique=True)


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))


class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    residency_id = db.Column(db.Integer, db.ForeignKey('residency_position.id'))
    rank = db.Column(db.Integer)  # 1 = highest preference


class ResidencyPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    year = db.Column(db.Integer, nullable=False)
    residency = db.Column(db.Text)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    num_of_residencies = db.Column(db.Integer)
    is_approved = db.Column(db.Boolean, default=False)
    company = db.relationship('Company', backref='residency_positions', lazy=True)
    salary= db.Column(db.Float)
    workplace_type = db.Column(db.String(100))


class CompanyAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    residency_id = db.Column(db.Integer, db.ForeignKey('residency_position.id'))
    title = db.Column(db.String(100))
    student = db.relationship('Student', backref='assignments', lazy=True)
    residency = db.relationship('ResidencyPosition', backref='assignments', lazy=True)
    company = db.relationship('Company', backref='company_assignments', lazy=True)


class ISEResidencyTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
