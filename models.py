from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    is_approved = db.Column(db.Boolean, default=False)

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
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

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
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    num_of_positions = db.Column(db.Integer)
    interview_required = db.Column(db.Boolean)
    

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
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    rank_score = db.Column(db.Integer)

class ResidencyPosition(db.Model):
    __tablename__ = 'residency_position'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    year = db.Column(db.Integer)
    num_of_residencies = db.Column(db.Integer)
    title = db.Column(db.String(100))  # <-- Add this line
    description = db.Column(db.Text)
    is_combined = db.Column(db.Boolean, default=False)

class CompanyAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))

class ISEResidencyTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
