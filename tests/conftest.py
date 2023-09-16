#!/usr/bin/python3

import os
import warnings

import pytest
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import risuspubl.api.authors
import risuspubl.api.books
import risuspubl.api.clients
import risuspubl.api.editors
import risuspubl.api.manuscripts
import risuspubl.api.sales_records
import risuspubl.api.salespeople
import risuspubl.api.series

from risuspubl.dbmodels import db
from risuspubl.flaskapp import create_app


# Set environment variable for Flask's configuration
os.environ[
    "FLASK_ENV"
] = "testing"  # This should be set before creating the app instance.


def pytest_sessionstart(session):
    # PostgreSQL server details
    HOST = "localhost"
    PORT = 5432
    TARGET_DATABASE = "risusp_test"
    TARGET_USER = "pguser"
    TARGET_PASSWORD = "pguser"  # Be careful with storing plaintext passwords!

    # Check for user existence by attempting to connect with the provided credentials
    try:
        # This connection will just use the default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=TARGET_USER,
            password=TARGET_PASSWORD,
            host=HOST,
            port=PORT,
        )
    except psycopg2.OperationalError as e:
        if (
            "password authentication failed" in str(e)
            or "role" in str(e)
            and "does not exist" in str(e)
        ):
            pytest.exit(
                f"The user '{TARGET_USER}' does not exist or wrong password provided. Please run ansible with setup_playbook.yml."
            )
        pytest.exit(f"Failed to connect to the PostgreSQL server. Error: {str(e)}")

    # If the above connection succeeded, the user exists. Now, check for the database's existence.
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM pg_database WHERE datname='{TARGET_DATABASE}'"
            )
            if not cursor.fetchone():
                pytest.exit(
                    f"The test database '{TARGET_DATABASE}' does not exist. Please run ansible with setup_playbook.yml."
                )
    finally:
        conn.close()


@pytest.fixture
def fresh_tables_db():
    yield db

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture(scope="session")
def staged_app_client():
    # Create the Flask app instance using the test config
    app = create_app(
        dict(
            SQLALCHEMY_DATABASE_URI=f"postgresql://pguser:pguser@localhost:5432/risusp_test"
        )
    )
    app_context = app.app_context()
    app_context.push()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield app, client

        db.session.commit()
        db.session.close()

        db.drop_all()

