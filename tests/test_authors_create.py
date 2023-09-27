#!/usr/bin/python3

import os
import random

from risuspubl.dbmodels import AuthorsBooks, AuthorsManuscripts

from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the POST /authors endpoint -- test 1 of 83
def test_author_create_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    author_dict = Genius.gen_author_dict()
    response = client.post("/authors", json=author_dict)

    DbBasedTester.test_author_resp(response, author_dict)

    DbBasedTester.cleanup__empty_all_tables()

    author_dict = Genius.gen_author_dict()
    author_dict.update(Genius.gen_book_dict())
    response = client.post("/authors", json=author_dict)
    assert response.status_code == 400, response.data.decode("utf8")


# Testing the POST /authors/<id>/books endpoint -- test 2 of 83
def test_create_author_book_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # Refactored test setup bc it's the same every time
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

    # Checking that authors_books bridge table row was created
    authors_books_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_id, book_id=book_obj.book_id)
        .first()
    )
    assert authors_books_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series_id
    author_id, book_dict = _setup()

    series_obj = Genius.gen_series_obj()
    book_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert book_dict["series_id"] == resp_jsobj["series_id"]
    assert book_dict["series_id"] == book_obj.series_id

    # Checking that authors_books bridge table row was created
    authors_books_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_id, book_id=book_obj.book_id)
        .first()
    )
    assert authors_books_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus id
    bogus_author_id = random.randint(1, 10)
    response = client.post(f"/authors/{bogus_author_id}/", json=book_dict)
    assert response.status_code == 404, response.data.decode("utf8")
    authors_books_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=bogus_author_id).first()
    )
    assert authors_books_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with including author_id in POSTed json
    author_id, book_dict = _setup()
    book_dict["author_id"] = author_id
    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    assert response.status_code == 400, response.data.decode("utf8")

    # Checking that authors_books bridge table row *wasn't* created
    authors_books_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_id).first()
    )
    assert authors_books_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with unexpected or missing parameters
    author_obj = Genius.gen_author_obj()
    author_dict = Genius.gen_author_dict()
    response = client.post(f"/authors/{author_obj.author_id}/books", json=author_dict)
    assert response.status_code == 400, response.data.decode("utf8")


# Testing the POST /authors/<id>/manuscripts endpoint -- test 3 of 83
def test_create_author_manuscript_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # Refactored test setup bc it's the same every time
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

    # Checking that authors_manuscripts bridge table row was created
    authors_manuscripts_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    assert authors_manuscripts_obj is not None

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

    # Checking that authors_manuscripts bridge table row was created
    authors_manuscripts_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    assert authors_manuscripts_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if bogus author_id is used
    bogus_author_id = random.randint(1, 10)
    response = client.post(
        f"/authors/{bogus_author_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    # Checking that authors_manuscripts bridge table row *wasn't* created
    authors_manuscripts_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_id).first()
    )
    assert authors_manuscripts_obj is None

    # Testing for 400 error with unexpected or missing parameters
    author_obj = Genius.gen_author_obj()
    author_dict = Genius.gen_author_dict()
    response = client.post(
        f"/authors/{author_obj.author_id}/manuscripts", json=author_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")


# Testing the POST /authors/<id>/metadata endpoint -- test 4 of 83
def test_create_author_metadata_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    # Refactored test setup bc it's the same every time
    def _setup(w_author_id=False):
        author_obj = Genius.gen_author_obj()
        if w_author_id:
            metadata_dict = Genius.gen_metadata_dict(author_obj.author_id)
        else:
            metadata_dict = Genius.gen_metadata_dict()
        return author_obj, metadata_dict

    # Testing base case
    author_obj, metadata_dict = _setup()
    response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )
    DbBasedTester.test_metadata_resp(response, metadata_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 if author_id is included in POSTed json
    author_obj, metadata_dict = _setup(w_author_id=True)
    response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 if the author_id is bogus
    metadata_dict = Genius.gen_metadata_dict()
    bogus_author_id = random.randint(1, 10)
    failed_response = client.post(
        f"/authors/{bogus_author_id}/metadata", json=metadata_dict
    )
    assert failed_response.status_code == 404

    # Testing for 400 error if missing or unexpected parameters are sent
    author_obj = Genius.gen_author_obj()
    author_dict = Genius.gen_author_dict()
    failed_response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=author_dict
    )
    assert failed_response.status_code == 400, failed_response.data


# Testing the POST /authors/<id>/<id>/books endpoint -- test 5 of 83
def test_create_authors_book_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # Refactored test setup bc it's the same every time
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

    # Checking that authors_books bridge table row was created
    author_no1_book_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no1_id, book_id=book_obj.book_id)
        .first()
    )
    author_no2_book_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no2_id, book_id=book_obj.book_id)
        .first()
    )
    assert author_no1_book_obj is not None
    assert author_no2_book_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with series id
    author_no1_id, author_no2_id, book_dict = _setup(w_series_id=True)
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    resp_jsobj, book_obj = DbBasedTester.test_book_resp(response, book_dict)
    assert book_dict["series_id"] == resp_jsobj["series_id"]
    assert book_dict["series_id"] == book_obj.series_id

    # Checking that authors_books bridge table row was created
    author_no1_book_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no1_id, book_id=book_obj.book_id)
        .first()
    )
    author_no2_book_obj = (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no2_id, book_id=book_obj.book_id)
        .first()
    )
    assert author_no1_book_obj is not None
    assert author_no2_book_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, first position
    author_no1_id, author_no2_id, book_dict = _setup()
    bogus_author_id = randint_excluding(1, 10, author_no1_id, author_no2_id)
    response = client.post(
        f"/authors/{author_no1_id}/{bogus_author_id}/books", json=book_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    # Checking that authors_books bridge table rows were created
    author_no1_book_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no1_id).first()
    )
    bogus_authors_books_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no1_id).first()
    )
    assert author_no1_book_obj is None
    assert bogus_authors_books_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, second position
    author_no1_id, author_no2_id, book_dict = _setup()
    bogus_author_id = randint_excluding(1, 10, author_no1_id, author_no2_id)
    response = client.post(
        f"/authors/{bogus_author_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    # Checking that authors_books bridge table rows were created
    bogus_authors_books_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no1_id).first()
    )
    author_no2_book_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no2_id).first()
    )
    assert bogus_authors_books_obj is None
    assert author_no2_book_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with unexpected property
    author_no1_id, author_no2_id, book_dict = _setup()
    book_dict["unexpected_prop"] = True
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")

    # Checking that authors_books bridge table rows *weren't* created
    author_no1_book_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no1_id).first()
    )
    author_no2_book_obj = (
        db.session.query(AuthorsBooks).filter_by(author_id=author_no2_id).first()
    )
    assert author_no1_book_obj is None
    assert author_no2_book_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with missing property
    author_no1_id, author_no2_id, book_dict = _setup()
    del book_dict["title"]
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error when author ids are equal
    author_no1_id, author_no2_id, book_dict = _setup()
    response = client.post(
        f"/authors/{author_no1_id}/{author_no1_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")


# Testing the POST /authors/<id>/<id>/manuscripts endpoint -- test 6 of 83
def test_create_authors_manuscript_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
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

    # Checking that authors_manuscripts bridge table rows were created
    author_no1_manuscript_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no1_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no2_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    assert author_no1_manuscript_obj is not None
    assert author_no2_manuscript_obj is not None

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

    # Checking that authors_manuscripts bridge table rows were created
    author_no1_manuscript_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no1_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no2_id, manuscript_id=manuscript_obj.manuscript_id)
        .first()
    )
    assert author_no1_manuscript_obj is not None
    assert author_no2_manuscript_obj is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, first position
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    bogus_author_id = randint_excluding(1, 10, author_no1_id, author_no2_id)
    response = client.post(
        f"/authors/{author_no1_id}/{bogus_author_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    # Checking that authors_manuscripts bridge table rows *weren't* created
    author_no1_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no1_id).first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=bogus_author_id)
        .first()
    )
    assert author_no1_manuscript_obj is None
    assert author_no2_manuscript_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus author_id, second position
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    bogus_author_id = randint_excluding(1, 10, author_no1_id, author_no2_id)
    response = client.post(
        f"/authors/{bogus_author_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    # Checking that authors_manuscripts bridge table rows *weren't* created
    bogus_authors_manuscripts_obj = (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=bogus_author_id)
        .first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no2_id).first()
    )
    assert bogus_authors_manuscripts_obj is None
    assert author_no2_manuscript_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with unexpected property
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    manuscript_dict["unexpected_prop"] = True
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")

    # Checking that authors_manuscripts bridge table rows *weren't* created
    author_no1_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no1_id).first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no2_id).first()
    )
    assert author_no1_manuscript_obj is None
    assert author_no2_manuscript_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing with missing property
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    del manuscript_dict["working_title"]
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")

    # Checking that authors_manuscripts bridge table rows *weren't* created
    author_no1_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no1_id).first()
    )
    author_no2_manuscript_obj = (
        db.session.query(AuthorsManuscripts).filter_by(author_id=author_no2_id).first()
    )
    assert author_no1_manuscript_obj is None
    assert author_no2_manuscript_obj is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error when author ids are equal
    author_no1_id, author_no2_id, manuscript_dict = _setup()
    response = client.post(
        f"/authors/{author_no1_id}/{author_no1_id}/manuscripts", json=manuscript_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")
