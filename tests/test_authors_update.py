#!/usr/bin/python3

import os
import random

import pprint
import json
import pytest
from risuspubl.dbmodels import Author

from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the PATCH /authors/<id>/books/<id> endpoint
def test_update_author_book_endpoint(db_w_cleanup, staged_app_client):  # 25/83
    db = db_w_cleanup
    app, client = staged_app_client

    def _setup():
        author_obj = Genius.gen_author_obj()
        editor_obj = Genius.gen_editor_obj()
        book_obj = Genius.gen_book_obj(editor_obj.editor_id)
        authors_books_obj = Genius.gen_authors_books_obj(
            author_obj.author_id, book_obj.book_id
        )
        return author_obj, editor_obj, book_obj

    # Testing base case
    author_obj, editor_obj, book_obj = _setup()
    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    response = client.patch(f"/authors/{author_obj.author_id}/books/{book_obj.book_id}", json=book_dict)
    DbBasedTester.test_book_resp(response, book_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    author_obj, editor_obj, book_obj = _setup()
    response = client.patch(f"/authors/{author_obj.author_id}/books/{book_obj.book_id}", json={})
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if author_id is bogus
    author_obj, editor_obj, book_obj = _setup()
    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    assert author_obj is not None
    response = client.patch(f"/authors/{bogus_author_id}/books/{book_obj.book_id}", json=book_dict)
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if book_id is bogus
    author_obj, editor_obj, book_obj = _setup()
    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    bogus_book_id = randint_excluding(1, 10, book_obj.book_id)
    response = client.patch(f"/authors/{author_obj.author_id}/books/{bogus_book_id}", json=book_dict)
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    author_obj, editor_obj, book_obj = _setup()
    author_dict = Genius.gen_author_dict()
    bogus_book_id = randint_excluding(1, 10, book_obj.book_id)
    response = client.patch(f"/authors/{author_obj.author_id}/books/{bogus_book_id}", json=author_dict)
    assert response.status_code == 400, response.data


# # Testing the PATCH /authors/<id> endpoint
# def test_update_author_by_id_endpoint(db_w_cleanup, staged_app_client):  # 26/83
#     db = db_w_cleanup
#     app, client = staged_app_client
# 
#     author_obj = Genius.gen_author_obj()
# 
# 
# # Testing the PATCH /authors/<id>/manuscripts/<id> endpoint
# def test_update_author_manuscript_endpoint(db_w_cleanup, staged_app_client):  # 27/83
#     db = db_w_cleanup
#     app, client = staged_app_client
# 
#     author_obj = Genius.gen_author_obj()
# 
# 
# # Testing the PATCH /authors/<id>/metadata endpoint
# def test_update_author_metadata_endpoint(db_w_cleanup, staged_app_client):  # 28/83
#     db = db_w_cleanup
#     app, client = staged_app_client
# 
#     author_obj = Genius.gen_author_obj()
#     metadata_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
# 
# 
# # Testing the PATCH /authors/<id>/<id>/books/<id> endpoint
# def test_update_authors_book_endpoint(db_w_cleanup, staged_app_client):  # 29/83
#     db = db_w_cleanup
#     app, client = staged_app_client
# 
#     author_no1_obj = Genius.gen_author_obj()
#     author_no2_obj = Genius.gen_author_obj()
#     book_obj = Genius.gen_book_obj()
#     authors_books_obj = Genius.gen_authors_books_obj(
#         author_no1_obj.author_id, book_obj.book_id
#     )
#     authors_books_obj = Genius.gen_authors_books_obj(
#         author_no2_obj.author_id, book_obj.book_id
#     )
# 
# 
# # Testing the PATCH /authors/<id>/<id>/manuscripts/<id> endpoint
# def test_update_authors_manuscript_endpoint(db_w_cleanup, staged_app_client):  # 30/83
#     db = db_w_cleanup
#     app, client = staged_app_client
# 
#     author_obj = Genius.gen_author_obj()
