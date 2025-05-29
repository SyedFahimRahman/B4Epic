from flask import Blueprint, jsonify, request
from models import Company, ResidencyPosition, Preference, Student
from extensions import db

api_bp = Blueprint('api' , __name__)        #creates a group of api routes & this blueprint will be registered later in app.py

@api_bp.route('/companies', methods=['GET'])        #when someone goes to /companies using GET request (URL), this runs the next function
def get_companies():
    try:
        companies = Company.query.all()     #fetches all company records from database
        return jsonify([
        {"id": c.id, "name": c.name} for c in companies   #turns each company object into a simple dictionary
    ])                                                  #sends that list to the browser in JSON format
    except Exception as e:
        print(f"error fetching companies: {e} ")
        return jsonify({"error": "error fetching companies"}), 500


@api_bp.route('/residency_positions', methods=['GET'])
def get_residency_positions():
    residencies = ResidencyPosition.query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "company" : r.company_id} for r in residencies

    ])

@api_bp.route('/preferences', methods=['POST'])
def submit_preferences():
    data = request.get_json()
    student_id = data.get('student_id')
    preferences = data.get('preferences')

    if not student_id or not preferences:
        return jsonify({'error': 'Missing student_id or preferences'}), 400

    #validate student exits
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    #clear existing preferences for the student
    Preference.query.filter_by(student_id= student_id).delete()

    #insert new preferences:
    for pref in preferences:
        company_id = pref.get('company_id')
        rank = pref.get('rank')

        if company_id is None or rank is None:
            continue        #skips invalid entry

        new_pref = Preference(student_id=student_id, company_id=company_id, preference_rank=rank)
        db.session.add(new_pref)

    db.session.commit()
    return jsonify({'message': 'Preferences submitted successfully'})


