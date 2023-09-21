#!/usr/bin/python3

import os
import random

import pprint
import json
import pytest
from risuspubl.dbmodels import Author

from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the GET /authors/<id>/books/<id> endpoint
def test_display_author_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 13/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    authors_books_obj = Genius.gen_authors_books_obj(
        author_obj.author_id, book_obj.book_id
    )

    response = client.get(f"/authors/{author_obj.author_id}/books/{book_obj.book_id}")
    assert response.status_code == 200
    DbBasedTester.test_book_resp(response, book_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}/books/{bogus_book_id}")
    assert response.status_code == 404

## Testing the GET /authors/<id>/books endpoint
#def test_display_author_books_endpoint(db_w_cleanup, staged_app_client):  # 14/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
#    author_obj = Genius.gen_author_obj()
#    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
#    authors_books_objs_l = [
#        Genius.gen_authors_books_obj(author_obj.author_id, book_obj.book_id)
#        for book_obj in books_objs_l
#    ]
#
#    response = client.get(f"/authors/{author_obj.author_id}/books/{book_obj.book_id}")
#
#    DbBasedTester.test_book_resp(response, book_obj)
#

# Testing the GET /authors/<id> endpoint
# def test_display_author_by_id_endpoint(db_w_cleanup, staged_app_client): # 15/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/manuscripts/<id> endpoint
# def test_display_author_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client): # 16/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/manuscripts endpoint
# def test_display_author_manuscripts_endpoint(db_w_cleanup, staged_app_client): # 17/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/metadata endpoint
# def test_display_author_metadata_endpoint(db_w_cleanup, staged_app_client): # 18/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/<id>/books/<id> endpoint
# def test_display_authors_book_by_id_endpoint(db_w_cleanup, staged_app_client): # 19/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/<id>/books endpoint
# def test_display_authors_books_endpoint(db_w_cleanup, staged_app_client): # 20/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/<id> endpoint
# def test_display_authors_by_ids_endpoint(db_w_cleanup, staged_app_client): # 21/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/<id>/manuscripts/<id> endpoint
# def test_display_authors_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client): # 22/83
#   db = db_w_cleanup
#   app, client = staged_app_client

# Testing the GET /authors/<id>/<id>/manuscripts endpoint
# def test_display_authors_manuscripts_endpoint(db_w_cleanup, staged_app_client): # 23/83
#   db = db_w_cleanup
#   app, client = staged_app_client
