#!/usr/bin/python3

import os
import random

from risuspubl.dbmodels import (
    Author,
    AuthorsBooks,
    Book,
)
from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the DELETE /books/<id> endpoint -- test 31 of 84
def test_delete_book_by_id_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_id, book_id)
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200, response.data.decode("utf8")
    assert response.get_json() is True
    assert db.session.query(Author).get(author_id) is not None
    assert db.session.query(Book).get(book_id) is None
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_id, book_id=book_id)
        .first()
    ) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus book_id
    bogus_book_id = random.randint(1, 10)
    response = client.delete(f"/books/{bogus_book_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing the GET /books/<id> endpoint -- test 32 of 84
def test_display_book_by_id_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    response = client.get(f"/books/{book_obj.book_id}")
    DbBasedTester.test_book_resp(response, book_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus book_id
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/books/{bogus_book_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing the GET /books endpoint -- test 33 of 84
def test_index_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    editor_obj = Genius.gen_editor_obj()
    book_objs_l = list()
    for _ in range(3):
        book_obj = Genius.gen_book_obj(editor_obj.editor_id)
        book_objs_l.append(book_obj)
        Genius.gen_authors_books_obj(author_obj.author_id, book_obj.book_id)
    response = client.get("/books")
    assert response.status_code == 200, response.data.decode("utf8")
    for book_jsobj in response.get_json():
        assert any(
            book_jsobj["edition_number"] == book_obj.edition_number
            and book_jsobj["editor_id"] == book_obj.editor_id
            and book_jsobj["is_in_print"] == book_obj.is_in_print
            and book_jsobj["publication_date"] == book_obj.publication_date.isoformat()
            and book_jsobj["title"] == book_obj.title
            for book_obj in book_objs_l
        )


# Testing the PATCH /books/<id> endpoint -- test 34 of 84
def test_update_book_by_id_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    # Testing base case
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    response = client.patch(f"/books/{book_obj.book_id}", json=book_dict)
    DbBasedTester.test_book_resp(response, book_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    response = client.patch(f"/books/{book_obj.book_id}", json={})
    assert response.status_code == 400, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if book_id is bogus
    bogus_book_id = random.randint(1, 10)
    book_dict = Genius.gen_book_dict()
    response = client.patch(f"/books/{bogus_book_id}", json=book_dict)
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    author_dict = Genius.gen_author_dict()
    response = client.patch(f"/books/{book_obj.book_id}", json=author_dict)
    assert response.status_code == 400, response.data.decode("utf8")
