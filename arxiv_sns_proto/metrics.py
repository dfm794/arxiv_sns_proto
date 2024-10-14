from flask import Blueprint, render_template

bp = Blueprint('metrics', __name__)

@bp.route('/healthcheck')
def healthcheck():
    return render_template('healthcheck.html')
