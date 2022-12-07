#!/usr/bin/python3

import os

import flask

from .api import authors, books, clients, editors, manuscripts, salespeople, sales_records, series
from .dbmodels import db


def create_app(test_config=None):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='postgresql://postgres@localhost:5432/risuspublishing',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)

    app.register_blueprint(authors.blueprint)
    app.register_blueprint(books.blueprint)
    app.register_blueprint(manuscripts.blueprint)
    app.register_blueprint(clients.blueprint)
    app.register_blueprint(editors.blueprint)
    app.register_blueprint(salespeople.blueprint)
    app.register_blueprint(series.blueprint)
    app.register_blueprint(sales_records.blueprint)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app
