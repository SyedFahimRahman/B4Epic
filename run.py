from extensions import db
from app import app
import models


with app.app_context():
    db.create_all()
    print("All tables created successfully.")