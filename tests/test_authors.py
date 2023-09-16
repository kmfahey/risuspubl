#!/usr/bin/python3

import os

import pytest
import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, downgrade

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
os.environ["FLASK_ENV"] = "testing"  # This should be set before creating the app instance.


def test_author_create_endpoint(db_setup_teardown):
    pass

# def test_create_author_book_endpoint

# def test_create_author_manuscript_endpoint

# def test_create_author_metadata_endpoint

# def test_create_authors_book_endpoint

# def test_create_authors_manuscript_endpoint

# def test_delete_author_book_endpoint

# def test_delete_author_by_id_endpoint

# def test_delete_author_manuscript_endpoint

# def test_delete_author_metadata_endpoint

# def test_delete_authors_book_endpoint

# def test_delete_authors_manuscript_endpoint

# def test_display_author_book_by_id_endpoint

# def test_display_author_books_endpoint

# def test_display_author_by_id_endpoint

# def test_display_author_manuscript_by_id_endpoint

# def test_display_author_manuscripts_endpoint

# def test_display_author_metadata_endpoint

# def test_display_authors_book_by_id_endpoint

# def test_display_authors_books_endpoint

# def test_display_authors_by_ids_endpoint

# def test_display_authors_manuscript_by_id_endpoint

# def test_display_authors_manuscripts_endpoint

# def test_index_endpoint

# def test_update_author_book_endpoint

# def test_update_author_by_id_endpoint

# def test_update_author_manuscript_endpoint

# def test_update_author_metadata_endpoint

# def test_update_authors_book_endpoint

# def test_update_authors_manuscript_endpoint
