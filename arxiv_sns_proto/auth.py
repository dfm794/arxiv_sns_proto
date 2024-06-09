import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

import psycopg2
from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Routines for logging in, registering, and logging out
# Routines were derived from the flask tutorial at https://flask.palletsprojects.com/en/2.3.x/tutorial/

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        db.execute(
            'SELECT * FROM "user" WHERE username = (%s)', (username,)
        )
        user = db.fetchone()

        if user is None:
            error = 'Incorrect username.'
        #elif not check_password_hash(user['password'], password):
        elif not check_password_hash(user[2], password):

            error = 'Incorrect password.'

        g.user = None
        if error is None:
            session.clear()
            #session['user_id'] = user['id']
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO "user" (username, password) VALUES (%s, %s)',
                    (username, generate_password_hash(password)),
                )
                db.connection.commit()
            except psycopg2.errors.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        get_db().execute(
            'SELECT * FROM "user" WHERE id = (%s)', (user_id,)
        )
        g.user = db.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

