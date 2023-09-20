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


def test_author_create_endpoint(db_w_cleanup, staged_app_client):  # 1/83
    app, client = staged_app_client

    author_dict = Genius.gen_author_dict()
    response = client.post("/authors", json=author_dict)

    DbBasedTester.test_author_resp(response, author_dict)


def test_create_author_book_endpoint(db_w_cleanup, staged_app_client):  # 2/83
    app, client = staged_app_client

    def _setup():
        author_obj = Genius.gen_author_obj()
        editor_obj = Genius.gen_editor_obj()

        book_dict = Genius.gen_book_dict(editor_obj.editor_id)

        return author_obj.author_id, book_dict

    author_id, book_dict = _setup()

    # Testing without series_id
    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] is None
    assert book_obj.series_id is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series_id
    author_id, book_dict = _setup()

    series_obj = Genius.gen_series_obj()
    book_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert book_dict["series_id"] == resp_jsobj["series_id"]
    assert book_dict["series_id"] == book_obj.series_id

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus id
    bogus_author_id = random.randint(1, 10)
    response = client.post(f"/authors/{bogus_author_id}/", json=book_dict)
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with including author_id in POSTed json
    author_id, book_dict = _setup()

    book_dict["author_id"] = author_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    assert response.status_code == 400


def test_create_author_manuscript_endpoint(db_w_cleanup, staged_app_client):  # 3/83
    app, client = staged_app_client

    def _setup():
        author_obj = Genius.gen_author_obj()
        editor_obj = Genius.gen_editor_obj()

        manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)

        return author_obj.author_id, manuscript_dict

    author_id, manuscript_dict = _setup()

    # Testing without series_id
    response = client.post(f"/authors/{author_id}/manuscripts", json=manuscript_dict)
    resp_jsobj, manuscript_obj = DbBasedTester.test_manuscript_resp(
        response, manuscript_dict
    )
    assert resp_jsobj["series_id"] is None
    assert manuscript_obj.series_id is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series_id
    author_id, manuscript_dict = _setup()

    series_obj = Genius.gen_series_obj()
    manuscript_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/manuscripts", json=manuscript_dict)
    resp_jsobj, manuscript_obj = DbBasedTester.test_manuscript_resp(
        response, manuscript_dict
    )
    assert manuscript_dict["series_id"] == resp_jsobj["series_id"]
    assert manuscript_dict["series_id"] == manuscript_obj.series_id

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.post(f"/authors/{bogus_author_id}/", json=manuscript_dict)
    assert response.status_code == 404


def test_create_author_metadata_endpoint(db_w_cleanup, staged_app_client):  # 4/83
    app, client = staged_app_client

    def _setup(w_author_id=False):
        author_obj = Genius.gen_author_obj()
        if w_author_id:
            metadata_dict = Genius.gen_author_metadata_dict(author_obj.author_id)
        else:
            metadata_dict = Genius.gen_author_metadata_dict()
        return author_obj, metadata_dict

    author_obj, metadata_dict = _setup()
    response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )
    DbBasedTester.test_metadata_resp(response, metadata_dict)

    DbBasedTester.cleanup__empty_all_tables()

    author_obj, metadata_dict = _setup(w_author_id=True)
    response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )
    assert response.status_code == 400

    DbBasedTester.cleanup__empty_all_tables()

    metadata_dict = Genius.gen_author_metadata_dict()
    bogus_author_id = random.randint(1, 10)
    failed_response = client.post(
        f"/authors/{bogus_author_id}/metadata", json=metadata_dict
    )
    assert failed_response.status_code == 404


def test_create_authors_book_endpoint(db_w_cleanup, staged_app_client):  # 5/83
    app, client = staged_app_client

    def _setup(w_series_id=False):
        author_obj_no1 = Genius.gen_author_obj()
        author_obj_no2 = Genius.gen_author_obj()
        editor_obj = Genius.gen_editor_obj()

        if w_series_id:
            series_obj = Genius.gen_series_obj()
            book_dict = Genius.gen_book_dict(editor_obj.editor_id, series_obj.series_id)
        else:
            book_dict = Genius.gen_book_dict(editor_obj.editor_id)

        return author_obj_no1.author_id, author_obj_no2.author_id, book_dict

    # Testing without series id

    author_no1_id, author_no2_id, book_dict = _setup()
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] is None
    assert book_obj.series_id is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series id
    author_no1_id, author_no2_id, book_dict = _setup(w_series_id=True)
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert book_dict["series_id"] == resp_jsobj["series_id"]
    assert book_dict["series_id"] == book_obj.series_id

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, first position
    author_no1_id, author_no2_id, book_dict = _setup()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_id or bogus_author_id == author_no2_id:
        bogus_author_id = random.randint(1, 10)
    response = client.post(
        f"/authors/{author_no1_id}/{bogus_author_id}/books", json=book_dict
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, second position
    author_no1_id, author_no2_id, book_dict = _setup()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_id or bogus_author_id == author_no2_id:
        bogus_author_id = random.randint(1, 10)
    response = client.post(
        f"/authors/{bogus_author_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with unexpected property
    author_no1_id, author_no2_id, book_dict = _setup()
    book_dict["unexpected_prop"] = True
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with missing property
    author_no1_id, author_no2_id, book_dict = _setup()
    del book_dict["title"]
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data


def test_create_authors_manuscript_endpoint(db_w_cleanup, staged_app_client):  # 6/83
    app, client = staged_app_client

    def _setup(w_series_id=False):
        author_obj_no1 = Genius.gen_author_obj()
        author_obj_no2 = Genius.gen_author_obj()
        editor_obj = Genius.gen_editor_obj()

        if w_series_id:
            series_obj = Genius.gen_series_obj()
            manuscript_dict = Genius.gen_manuscript_dict(
                editor_obj.editor_id, series_obj.series_id
            )
        else:
            manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)

        return author_obj_no1.author_id, author_obj_no2.author_id, manuscript_dict

    # Testing without series id
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    resp_jsobj, manuscript_obj = DbBasedTester.test_manuscript_resp(
        response, manuscript_dict
    )
    assert resp_jsobj["series_id"] is None
    assert manuscript_obj.series_id is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series id
    author_no1_id, author_no2_id, manuscript_dict = _setup(w_series_id=True)
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    resp_jsobj, manuscript_obj = DbBasedTester.test_manuscript_resp(
        response, manuscript_dict
    )
    assert manuscript_dict["series_id"] == resp_jsobj["series_id"]
    assert manuscript_dict["series_id"] == manuscript_obj.series_id

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, first position
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_id or bogus_author_id == author_no2_id:
        bogus_author_id = random.randint(1, 10)
    response = client.post(
        f"/authors/{author_no1_id}/{bogus_author_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, second position
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    bogus_author_id = random.randint(1, 10)
    while bogus_author_id == author_no1_id or bogus_author_id == author_no2_id:
        bogus_author_id = random.randint(1, 10)
    response = client.post(
        f"/authors/{bogus_author_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with unexpected property
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    manuscript_dict["unexpected_prop"] = True
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with missing property
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    del manuscript_dict["working_title"]
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 400, response.data


# def test_delete_author_book_endpoint # 7/83

# def test_delete_author_by_id_endpoint # 8/83

# def test_delete_author_manuscript_endpoint # 9/83

# def test_delete_author_metadata_endpoint # 10/83

# def test_delete_authors_book_endpoint # 11/83

# def test_delete_authors_manuscript_endpoint # 12/83

# def test_display_author_book_by_id_endpoint # 13/83

# def test_display_author_books_endpoint # 14/83

# def test_display_author_by_id_endpoint # 15/83

# def test_display_author_manuscript_by_id_endpoint # 16/83

# def test_display_author_manuscripts_endpoint # 17/83

# def test_display_author_metadata_endpoint # 18/83

# def test_display_authors_book_by_id_endpoint # 19/83

# def test_display_authors_books_endpoint # 20/83

# def test_display_authors_by_ids_endpoint # 21/83

# def test_display_authors_manuscript_by_id_endpoint # 22/83

# def test_display_authors_manuscripts_endpoint # 23/83


def test_index_endpoint(db_w_cleanup, staged_app_client):  # 24/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_dicts = [Genius.gen_author_dict() for _ in range(10)]
    for author_dict in author_dicts:
        db.session.add(Author(**author_dict))
    db.session.commit()
    response = client.get("/authors")
    assert response.status_code == 200
    for author_jsobj in response.get_json():
        assert any(
            author_dict["first_name"] == author_jsobj["first_name"]
            and author_dict["last_name"] == author_jsobj["last_name"]
            for author_dict in author_dicts
        )


# def test_update_author_book_endpoint # 25/83

# def test_update_author_by_id_endpoint # 26/83

# def test_update_author_manuscript_endpoint # 27/83

# def test_update_author_metadata_endpoint # 28/83

# def test_update_authors_book_endpoint # 29/83

# def test_update_authors_manuscript_endpoint # 30/83
