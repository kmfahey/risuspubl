#!/usr/bin/python3

import os
import random

import pprint
import json
import pytest
import operator
import itertools

from conftest import Genius, DbBasedTester
from risuspubl.dbmodels import Author


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


# Testing the GET /authors/<id>/books endpoint
def test_display_author_books_endpoint(db_w_cleanup, staged_app_client):  # 14/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
    authors_books_objs_l = [
        Genius.gen_authors_books_obj(author_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]

    response = client.get(f"/authors/{author_obj.author_id}/books")
    assert response.status_code == 200
    book_jsobj_l = json.loads(response.data)
    book_jsobj_obj_matches = dict()
    for book_obj in book_objs_l:
        book_jsobj_obj_matches[book_obj.book_id] = operator.concat(
            [book_obj],
            list(
                filter(
                    lambda jsobj: jsobj["book_id"] == book_obj.book_id,
                    book_jsobj_l,
                )
            ),
        )

    for _, (book_obj, book_jsobj) in book_jsobj_obj_matches.items():
        assert book_jsobj["edition_number"] == book_obj.edition_number
        assert book_jsobj["editor_id"] == book_obj.editor_id
        assert book_jsobj["is_in_print"] == book_obj.is_in_print
        assert book_jsobj["publication_date"] == book_obj.publication_date.isoformat()
        assert book_jsobj["title"] == book_obj.title

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}/books")
    assert response.status_code == 404


#  Testing the GET /authors/<id> endpoint
def test_display_author_by_id_endpoint(db_w_cleanup, staged_app_client):  # 15/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()

    response = client.get(f"/authors/{author_obj.author_id}")
    DbBasedTester.test_author_resp(response, author_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}")
    assert response.status_code == 404


# Testing the GET /authors/<id>/manuscripts/<id> endpoint
def test_display_author_manuscript_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 16/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    authors_manuscripts_obj = Genius.gen_authors_manuscripts_obj(
        author_obj.author_id, manuscript_obj.manuscript_id
    )

    response = client.get(
        f"/authors/{author_obj.author_id}/manuscripts/{manuscript_obj.manuscript_id}"
    )
    assert response.status_code == 200
    DbBasedTester.test_manuscript_resp(response, manuscript_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    bogus_manuscript_id = random.randint(1, 10)
    response = client.get(
        f"/authors/{bogus_author_id}/manuscripts/{bogus_manuscript_id}"
    )
    assert response.status_code == 404


# Testing the GET /authors/<id>/manuscripts endpoint
def test_display_author_manuscripts_endpoint(db_w_cleanup, staged_app_client):  # 17/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    manuscript_objs_l = [Genius.gen_manuscript_obj() for _ in range(3)]
    authors_manuscripts_objs_l = [
        Genius.gen_authors_manuscripts_obj(
            author_obj.author_id, manuscript_obj.manuscript_id
        )
        for manuscript_obj in manuscript_objs_l
    ]

    response = client.get(f"/authors/{author_obj.author_id}/manuscripts")
    assert response.status_code == 200
    manuscript_jsobj_l = json.loads(response.data)
    manuscript_jsobj_obj_matches = dict()
    for manuscript_obj in manuscript_objs_l:
        manuscript_jsobj_obj_matches[manuscript_obj.manuscript_id] = operator.concat(
            [manuscript_obj],
            list(
                filter(
                    lambda jsobj: jsobj["manuscript_id"]
                    == manuscript_obj.manuscript_id,
                    manuscript_jsobj_l,
                )
            ),
        )

    for _, (manuscript_obj, manuscript_jsobj) in manuscript_jsobj_obj_matches.items():
        assert manuscript_jsobj["editor_id"] == manuscript_obj.editor_id
        assert manuscript_jsobj["working_title"] == manuscript_obj.working_title
        assert manuscript_jsobj["due_date"] == manuscript_obj.due_date.isoformat()
        assert manuscript_jsobj["advance"] == manuscript_obj.advance

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}/manuscripts")
    assert response.status_code == 404


# Testing the GET /authors/<id>/metadata endpoint
def test_display_author_metadata_endpoint(db_w_cleanup, staged_app_client):  # 18/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    metadata_obj = Genius.gen_author_metadata_obj(author_obj.author_id)

    response = client.get(f"/authors/{author_obj.author_id}/metadata")
    DbBasedTester.test_metadata_resp(response, metadata_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}/metadata")
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    author_obj = Genius.gen_author_obj()
    metadata_no1_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
    metadata_no2_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
    response = client.get(f"/authors/{author_obj.author_id}/metadata")
    assert response.status_code == 500


# Testing the GET /authors/<id>/<id>/books/<id> endpoint
def test_display_authors_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 19/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    authors_no1_books_obj = Genius.gen_authors_books_obj(
        author_no1_obj.author_id, book_obj.book_id
    )
    authors_no2_books_obj = Genius.gen_authors_books_obj(
        author_no2_obj.author_id, book_obj.book_id
    )
    response = client.get(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{book_obj.book_id}"
    )
    DbBasedTester.test_book_resp(response, book_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the 1st author_id is bogus
    author_no2_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no2_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    book_obj = Genius.gen_book_obj()
    authors_no2_books_obj = Genius.gen_authors_books_obj(
        author_no2_obj.author_id, book_obj.book_id
    )
    response = client.get(
        f"/authors/{bogus_author_id}"
        + f"/{author_no2_obj.author_id}/books/{book_obj.book_id}"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the 2nd author_id is bogus
    author_no1_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    book_obj = Genius.gen_book_obj()
    authors_no1_books_obj = Genius.gen_authors_books_obj(
        author_no1_obj.author_id, book_obj.book_id
    )
    response = client.get(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{bogus_author_id}/books/{book_obj.book_id}"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the book_id is bogus
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    bogus_book_id = random.randint(1, 10)
    response = client.get(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{bogus_book_id}"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error when both author_ids in endpoint url are equal
    author_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    authors_books_obj = Genius.gen_authors_books_obj(
        author_obj.author_id, book_obj.book_id
    )
    response = client.get(
        f"/authors/{author_obj.author_id}/{author_obj.author_id}/books/{book_obj.book_id}"
    )
    assert response.status_code == 400


# Testing the GET /authors/<id>/<id>/books endpoint
def test_display_authors_books_endpoint(db_w_cleanup, staged_app_client):  # 20/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
    authors_no1_books_objs_l = [
        Genius.gen_authors_books_obj(author_no1_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]
    authors_no2_books_objs_l = [
        Genius.gen_authors_books_obj(author_no2_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]
    response = client.get(
        f"/authors/{author_no1_obj.author_id}/{author_no2_obj.author_id}/books"
    )
    assert response.status_code == 200
    book_jsobj_l = json.loads(response.data)
    book_jsobj_obj_matches = dict()
    for book_obj in book_objs_l:
        book_jsobj_obj_matches[book_obj.book_id] = operator.concat(
            [book_obj],
            list(
                filter(
                    lambda jsobj: jsobj["book_id"] == book_obj.book_id,
                    book_jsobj_l,
                )
            ),
        )

    for _, (book_obj, book_jsobj) in book_jsobj_obj_matches.items():
        assert book_jsobj["edition_number"] == book_obj.edition_number
        assert book_jsobj["editor_id"] == book_obj.editor_id
        assert book_jsobj["is_in_print"] == book_obj.is_in_print
        assert book_jsobj["publication_date"] == book_obj.publication_date.isoformat()
        assert book_jsobj["title"] == book_obj.title

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for a 404 error when the 1st author_id is bogus
    author_no1_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
    authors_no1_books_objs_l = [
        Genius.gen_authors_books_obj(author_no1_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]
    response = client.get(
        f"/authors/{author_no1_obj.author_id}/{bogus_author_id}/books"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for a 404 error when the 2nd author_id is bogus
    author_no2_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no2_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
    authors_no2_books_objs_l = [
        Genius.gen_authors_books_obj(author_no2_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]
    response = client.get(
        f"/authors/{bogus_author_id}/{author_no2_obj.author_id}/books"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error when both author_ids are identical
    author_obj = Genius.gen_author_obj()
    book_objs_l = [Genius.gen_book_obj() for _ in range(3)]
    authors_books_objs_l = [
        Genius.gen_authors_books_obj(author_obj.author_id, book_obj.book_id)
        for book_obj in book_objs_l
    ]
    response = client.get(
        f"/authors/{author_obj.author_id}/{author_obj.author_id}/books"
    )
    assert response.status_code == 400


# Testing the GET /authors/<id>/<id> endpoint
def test_display_authors_by_ids_endpoint(db_w_cleanup, staged_app_client):  # 21/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    response = client.get(
        f"/authors/{author_no1_obj.author_id}/{author_no2_obj.author_id}"
    )
    assert response.status_code == 200
    resp_jsobj = response.get_json()
    author_no1_jsobj = resp_jsobj[0]
    author_no2_jsobj = resp_jsobj[1]
    assert author_no1_obj.first_name == author_no1_jsobj["first_name"]
    assert author_no1_obj.last_name == author_no1_jsobj["last_name"]
    assert author_no2_obj.first_name == author_no2_jsobj["first_name"]
    assert author_no2_obj.last_name == author_no2_jsobj["last_name"]

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when 1st author_id is bogus
    author_no2_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no2_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{bogus_author_id}/{author_no2_obj.author_id}")
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when 2nd author_id is bogus
    author_no1_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{author_no1_obj.author_id}/{bogus_author_id}")
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    author_no1_obj = Genius.gen_author_obj()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_obj.author_id:
        bogus_author_id = random.randint(1, 10)
    response = client.get(f"/authors/{author_no1_obj.author_id}/{bogus_author_id}")
    assert response.status_code == 404


# Testing the GET /authors/<id>/<id>/manuscripts/<id> endpoint
def test_display_authors_manuscript_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 22/83
    db = db_w_cleanup
    app, client = staged_app_client


# Testing the GET /authors/<id>/<id>/manuscripts endpoint
# def test_display_authors_manuscripts_endpoint(db_w_cleanup, staged_app_client): # 23/83
#   db = db_w_cleanup
#   app, client = staged_app_client
