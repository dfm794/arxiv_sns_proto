# This file originally derived from the flask tutorial
# https://flask.palletsprojects.com/en/2.3.x/tutorial/


#import sqlite3
import psycopg2
import psycopg2.extras

import os
import click
from flask import current_app, g


#below is the original get_db() function for sqlite3
# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db

#below is the modified get_db() function for postgresql
def get_db():
    if 'db' not in g:
        db_url = os.environ.get('DATABASE_URL', default=None)
        if db_url is not None:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
            #current_app.config['DATABASE']
            )
        #g.db.row_factory = sqlite3.Row
        g.db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    