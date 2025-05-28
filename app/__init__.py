from flask import Flask
from extensions import db
import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.public_routes import public_bp
    from app.routes.allocations_routes import allocation_bp
    from app.routes.students_routes import student_bp
    from app.routes.company_routes import company_bp




    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(allocation_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)

    return app