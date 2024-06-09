from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('searches', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    print(f'g.user: {g.user}')
    db.execute(
        'SELECT s.id, search_key, search_result, created, author_id, username'
        ' FROM search s JOIN "user" u ON s.author_id = u.id'
        ' WHERE author_id = (%s)'
        ' ORDER BY created DESC',
        (g.user[0],)
    )
    searches = db.fetchall()
    print(f'searches: {searches}')
    return render_template('searches/index.html', searches=searches)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        search_key = request.form['search_key']
        error = None

        if not search_key:
            error = 'Search Key is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO search (search_key, author_id)'
                ' VALUES (%s, %s)',
                (search_key, g.user[0])
            )
            db.connection.commit()
            return redirect(url_for('searches.index'))

    return render_template('searches/create.html')

def get_search(id, check_author=True):
    db = get_db()
    db.execute(
        'SELECT s.id, search_key, search_result, created, author_id, username'
        ' FROM search s JOIN "user" u ON s.author_id = u.id'
        ' WHERE s.id = (%s)',
        (id,)
    )
    search = db.fetchone()

    if search is None:
        abort(404, f"Search id {id} doesn't exist.")

    if check_author and search['author_id'] != g.user[0]:
        abort(403)

    return search

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    search = get_search(id)

    if request.method == 'POST':
        search_key = request.form['search_key']
        error = None

        if not search_key:
            error = 'Search Key is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE search SET search_key = (%s)'
                ' WHERE id = (%s)',
                (search_key, id)
            )
            db.connection.commit()
            return redirect(url_for('searches.index'))

    return render_template('searches/update.html', search=search)

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete(id):
    get_search(id)
    db = get_db()
    db.execute('DELETE FROM search WHERE id = (%s)', (id,))
    db.connection.commit()
    return redirect(url_for('searches.index'))


