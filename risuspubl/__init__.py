#!/usr/bin/python3

import os

import flask

import risuspubl.api

from risuspubl.dbmodels import db


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

    app.register_blueprint(risuspubl.api.authors.blueprint)
    app.register_blueprint(risuspubl.api.books.blueprint)
    app.register_blueprint(risuspubl.api.manuscripts.blueprint)
    app.register_blueprint(risuspubl.api.clients.blueprint)
    app.register_blueprint(risuspubl.api.editors.blueprint)
    app.register_blueprint(risuspubl.api.salespeople.blueprint)
    app.register_blueprint(risuspubl.api.series.blueprint)
    app.register_blueprint(risuspubl.api.sales_records.blueprint)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app
