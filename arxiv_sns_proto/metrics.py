from flask import Blueprint, render_template, Response
from .db import get_db

bp = Blueprint('metrics', __name__)

@bp.route('/healthcheck')
def healthcheck():
    return render_template('metrics/healthcheck.html')

@bp.route('/metrics')
def metrics():
    db = get_db()
    
    # Query total users
    db.execute('SELECT COUNT(*) FROM "user"')
    total_users = db.fetchone()[0]
    
    # Query total searches
    db.execute('SELECT COUNT(*) FROM search')
    total_searches = db.fetchone()[0]
    
    # Query total search results
    db.execute('SELECT COUNT(*) FROM search_result')
    total_search_results = db.fetchone()[0]
    
    # Format the metrics in Prometheus format
    metrics_output = f"""
# HELP total_users Total number of registered users
# TYPE total_users gauge
total_users {total_users}

# HELP total_searches Total number of searches performed
# TYPE total_searches gauge
total_searches {total_searches}

# HELP total_search_results Total number of search results
# TYPE total_search_results gauge
total_search_results {total_search_results}
"""
    
    return Response(metrics_output, mimetype='text/plain')
