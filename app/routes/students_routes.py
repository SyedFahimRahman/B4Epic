from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import ResidencyPosition, Preference
from extensions import db

student_bp = Blueprint('students', __name__)

""""@student_bp.route('/list', methods=['GET'])
def list():
    if session.get('logged_in'):"""


@student_bp.route('/rank-positions', methods=['GET', 'POST'])
def rank_positions():
    if session.get('role') != 'student':
        flash("Only students can rank positions.")
        return redirect(url_for('main.index'))

    positions = ResidencyPosition.query.all()
    if request.method == 'POST':
        ordered_ids = request.form.get('position_order').split(',')
        for rank, pos_id in enumerate(ordered_ids, start=1):
            pref = Preference(
                student_id=session['student_id'],
                company_id=ResidencyPosition.query.get(pos_id).company_id,
                preference_rank=rank
            )
            db.session.add(pref)
        db.session.commit()
        flash("Preferences saved!")
        return redirect(url_for('main.index'))
    return render_template('rank_positions.html', positions=positions)

@student_bp.route("/jobs")
def list_jobs():
    jobs = ResidencyPosition.query.all()
    return render_template("list_jobs.html", jobs=jobs)