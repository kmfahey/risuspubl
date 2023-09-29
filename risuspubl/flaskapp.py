#!/usr/bin/python3

import os
import flask

from risuspubl.api import (
    authors,
    books,
    clients,
    docroot,
    editors,
    manuscripts,
    sales_records,
    salespeople,
    series,
)
from risuspubl.dbmodels import db


API_MODULES = (
    authors,
    books,
    clients,
    docroot,
    editors,
    manuscripts,
    sales_records,
    salespeople,
    series,
)


def create_app(test_config=None):
    app = flask.Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        dict(
            SECRET_KEY="dev", SQLALCHEMY_ECHO=True, SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_mapping(
            dict(
                SQLALCHEMY_DATABASE_URI="postgresql://pguser:pguser@localhost:5432/risuspubl"
            )
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)

    for api_module in API_MODULES:
        app.register_blueprint(api_module.blueprint)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app
