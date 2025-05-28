from flask import Blueprint, jsonify
from models import Company, ResidencyPosition
from extensions import db

api_bp = Blueprint('api' , __name__)        #creates a group of api routes & this blueprint will be registered later in app.py

@api_bp.route('/companies', methods=['GET'])        #when someone goes to /companies using GET request (URL), this runs the next function

def get_companies():
    companies = Company.query.all()     #fetches all company records from database
    return jsonify([
        {"id": c.id, "name": c.name} for c in companies   #turns each company object into a simple dictionary
    ])                                                    #sends that list to the browser in JSON format

@api_bp.route('/residency_positions', methods=['GET'])
def get_residency_positions():
    residencies = ResidencyPosition.query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "company" : r.company_id} for r in residencies

    ])


