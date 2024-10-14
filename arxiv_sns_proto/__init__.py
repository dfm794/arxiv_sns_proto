#!/usr/bin/env python3
import os
from flask import Flask, request, render_template, g, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .db import get_db
from . import auth
from . import searches
from . import metrics

# This file originally derived from the flask tutorial
# and modified for the purposes of this project.

# create_app(.) is a simple factory function that creates a Flask app
# and forces the app entry point to be the search page. Note that the 
# search page will redirect to login if no user session exists.

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)

    app.register_blueprint(metrics.bp)

    app.register_blueprint(searches.bp)
    app.add_url_rule('/', endpoint='index')


    # a simple page that says hello
    @app.route('/live_check')
    def live_check():
        return 'Site is alive!'

    return app

app = create_app()



    
