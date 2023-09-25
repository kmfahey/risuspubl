#!/usr/bin/python3

import os
import random
import pprint
import json
import operator

import pytest

from risuspubl.dbmodels import (
    Book,
    Client,
    Editor,
    Manuscript,
    Salesperson,
)
from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing POST /editors
def test_create_editor_endpoint(db_w_cleanup, staged_app_client):  # 40/83
    app, client = staged_app_client

    editor_dict = Genius.gen_editor_dict()
    response = client.post("/editors", json=editor_dict)
    DbBasedTester.test_editor_resp(response, editor_dict)

    DbBasedTester.cleanup__empty_all_tables()

    author_dict = Genius.gen_author_dict()
    response = client.post("/editors", json=author_dict)
    assert response.status_code == 400, response.data


# Testing DELETE /editors/<id>/books/<id> endpoint
def test_delete_editor_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 41/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_id=editor_obj.editor_id)
    book_id = book_obj.book_id
    response = client.delete(f"/editors/{editor_obj.editor_id}/books/{book_id}")
    assert response.status_code == 200, response.data
    assert json.loads(response.data) is True
    assert db.session.query(Editor).get(editor_obj.editor_id) is not None
    assert db.session.query(Book).get(book_id) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error with bogus editor_id
    book_obj = Genius.gen_book_obj()
    bogus_editor_id = random.randint(1, 10)
    response = client.delete(f"/editors/{bogus_editor_id}/books/{book_obj.book_id}")
    assert response.status_code == 404
    assert db.session.query(Book).get(book_obj.book_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error with bogus book_id
    editor_obj = Genius.gen_editor_obj()
    bogus_book_id = random.randint(1, 10)
    response = client.delete(f"/editors/{editor_obj.editor_id}/books/{bogus_book_id}")
    assert response.status_code == 404
    assert db.session.query(Editor).get(editor_obj.editor_id) is not None


# Testing DELETE /editors/<id> endpoint
def test_delete_editor_by_id_endpoint(db_w_cleanup, staged_app_client):  # 42/83
    db = db_w_cleanup
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    editor_id = editor_obj.editor_id

    book_obj = Genius.gen_book_obj(editor_id)
    book_id = book_obj.book_id

    manuscript_obj = Genius.gen_manuscript_obj(editor_id)
    manuscript_id = manuscript_obj.manuscript_id

    response = client.delete(f"/editors/{editor_obj.editor_id}")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Editor).get(editor_id) is None
    assert db.session.query(Book).get(book_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    bogus_editor_id = random.randint(1, 10)
    response = client.delete(f"/editors/{bogus_editor_id}")
    assert response.status_code == 404


# Testing DELETE /editors/<id>/manuscripts/<id> endpoint
def test_delete_editor_manuscript_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 43/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_id=editor_obj.editor_id)
    manuscript_id = manuscript_obj.manuscript_id
    response = client.delete(
        f"/editors/{editor_obj.editor_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 200, response.data
    assert json.loads(response.data) is True
    assert db.session.query(Editor).get(editor_obj.editor_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error with bogus editor_id
    manuscript_obj = Genius.gen_manuscript_obj()
    bogus_editor_id = random.randint(1, 10)
    response = client.delete(
        f"/editors/{bogus_editor_id}/manuscripts/{manuscript_obj.manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Manuscript).get(manuscript_obj.manuscript_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error with bogus manuscript_id
    editor_obj = Genius.gen_editor_obj()
    bogus_manuscript_id = random.randint(1, 10)
    response = client.delete(
        f"/editors/{editor_obj.editor_id}/manuscripts/{bogus_manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Editor).get(editor_obj.editor_id) is not None


# Testing GET /editors/<id>/books/<id> endpoint
def test_display_editor_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 44/83
    app, client = staged_app_client

    # Testing base case
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    response = client.get(f"/editors/{editor_obj.editor_id}/books/{book_obj.book_id}")
    assert response.status_code == 200, response.data
    DbBasedTester.test_book_resp(response, book_obj)

    DbBasedTester.cleanup__empty_all_tables()

    editor_obj = Genius.gen_editor_obj()
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/editors/{editor_obj.editor_id}/books/{bogus_book_id}")
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    bogus_editor_id = random.randint(1, 10)
    book_obj = Genius.gen_book_obj()
    response = client.get(f"/editors/{bogus_editor_id}/books/{book_obj.book_id}")
    assert response.status_code == 404, response.data


# Testing GET /editors/<id>/books endpoint
def test_display_editor_books_endpoint(db_w_cleanup, staged_app_client): # 45/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_objs_l = [Genius.gen_book_obj(editor_obj.editor_id) for _ in range(3)]
    response = client.get(f"/editors/{editor_obj.editor_id}/books")
    assert response.status_code == 200, response.data
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

    for book_obj, book_jsobj in book_jsobj_obj_matches.values():
        assert book_jsobj["edition_number"] == book_obj.edition_number
        assert book_jsobj["editor_id"] == book_obj.editor_id
        assert book_jsobj["is_in_print"] == book_obj.is_in_print
        assert book_jsobj["publication_date"] == book_obj.publication_date.isoformat()
        assert book_jsobj["title"] == book_obj.title

    DbBasedTester.cleanup__empty_all_tables()

    bogus_editor_id = random.randint(1, 10)
    response = client.get(f"/editors/{bogus_editor_id}/books")
    assert response.status_code == 404, response.data


# Testing GET /editors/<id> endpoint
def test_display_editor_by_id_endpoint(db_w_cleanup, staged_app_client): # 46/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()

    response = client.get(f"/editors/{editor_obj.editor_id}")
    DbBasedTester.test_editor_resp(response, editor_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_editor_id = random.randint(1, 10)
    response = client.get(f"/editors/{bogus_editor_id}")
    assert response.status_code == 404, response.data


# Testing GET /editors/<id>/manuscripts/<id> endpoint
# def test_display_editor_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client): # 47/83
#    app, client = staged_app_client
#
#    # Testing base case
#    editor_obj = Genius.gen_editor_obj()
#    manuscript_obj = Genius.gen_manuscript_obj()
#    Genius.gen_editors_manuscripts_obj(
#        editor_obj.editor_id, manuscript_obj.manuscript_id
#    )
#    response = client.get(
#        f"/editors/{editor_obj.editor_id}/manuscripts/{manuscript_obj.manuscript_id}"
#    )
#    assert response.status_code == 200, response.data
#    DbBasedTester.test_manuscript_resp(response, manuscript_obj)
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    bogus_editor_id = random.randint(1, 10)
#    bogus_manuscript_id = random.randint(1, 10)
#    response = client.get(
#        f"/editors/{bogus_editor_id}/manuscripts/{bogus_manuscript_id}"
#    )
#    assert response.status_code == 404, response.data


# Testing GET /editors/<id>/manuscripts endpoint
# def test_display_editor_manuscripts_endpoint(db_w_cleanup, staged_app_client): # 48/83
#    app, client = staged_app_client
#
#    editor_obj = Genius.gen_editor_obj()
#    manuscript_objs_l = [Genius.gen_manuscript_obj() for _ in range(3)]
#    for manuscript_obj in manuscript_objs_l:
#        Genius.gen_editors_manuscripts_obj(
#            editor_obj.editor_id, manuscript_obj.manuscript_id
#        )
#    response = client.get(f"/editors/{editor_obj.editor_id}/manuscripts")
#    assert response.status_code == 200, response.data
#    manuscript_jsobj_l = json.loads(response.data)
#    manuscript_jsobj_obj_matches = dict()
#    for manuscript_obj in manuscript_objs_l:
#        manuscript_jsobj_obj_matches[manuscript_obj.manuscript_id] = operator.concat(
#            [manuscript_obj],
#            list(
#                filter(
#                    lambda jsobj: jsobj["manuscript_id"]
#                    == manuscript_obj.manuscript_id,
#                    manuscript_jsobj_l,
#                )
#            ),
#        )
#
#    for _, (manuscript_obj, manuscript_jsobj) in manuscript_jsobj_obj_matches.items():
#        assert manuscript_jsobj["editor_id"] == manuscript_obj.editor_id
#        assert manuscript_jsobj["working_title"] == manuscript_obj.working_title
#        assert manuscript_jsobj["due_date"] == manuscript_obj.due_date.isoformat()
#        assert manuscript_jsobj["advance"] == manuscript_obj.advance
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    bogus_editor_id = random.randint(1, 10)
#    response = client.get(f"/editors/{bogus_editor_id}/manuscripts")
#    assert response.status_code == 404, response.data


# Testing GET /editors endpoint
def test_index_endpoint(db_w_cleanup, staged_app_client):  # 49/83
    db = db_w_cleanup
    app, client = staged_app_client

    editor_dicts = [Genius.gen_editor_dict() for _ in range(10)]
    for editor_dict in editor_dicts:
        db.session.add(Editor(**editor_dict))
    db.session.commit()
    response = client.get("/editors")
    assert response.status_code == 200
    for editor_jsobj in response.get_json():
        assert any(
            editor_dict["first_name"] == editor_jsobj["first_name"]
            and editor_dict["last_name"] == editor_jsobj["last_name"]
            and editor_dict["salary"] == editor_jsobj["salary"]
            for editor_dict in editor_dicts
        )


# Testing PATCH /editors/<id>/books/<id> endpoint
# def test_update_editor_book_by_id_endpoint(db_w_cleanup, staged_app_client): # 50/83
#    app, client = staged_app_client
#
#    def _setup():
#        editor_obj = Genius.gen_editor_obj()
#        editor_obj = Genius.gen_editor_obj()
#        book_obj = Genius.gen_book_obj(editor_obj.editor_id)
#        Genius.gen_editors_books_obj(editor_obj.editor_id, book_obj.book_id)
#        return editor_obj, editor_obj, book_obj
#
#    # Testing base case
#    editor_obj, editor_obj, book_obj = _setup()
#    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/books/{book_obj.book_id}", json=book_dict
#    )
#    DbBasedTester.test_book_resp(response, book_dict)
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 400 error if PATCHed json is empty
#    editor_obj, editor_obj, book_obj = _setup()
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/books/{book_obj.book_id}", json={}
#    )
#    assert response.status_code == 400, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error if editor_id is bogus
#    editor_obj, editor_obj, book_obj = _setup()
#    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
#    bogus_editor_id = randint_excluding(1, 10, editor_obj.editor_id)
#    assert editor_obj is not None
#    response = client.patch(
#        f"/editors/{bogus_editor_id}/books/{book_obj.book_id}", json=book_dict
#    )
#    assert response.status_code == 404, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error if book_id is bogus
#    editor_obj, editor_obj, book_obj = _setup()
#    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
#    bogus_book_id = randint_excluding(1, 10, book_obj.book_id)
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/books/{bogus_book_id}", json=book_dict
#    )
#    assert response.status_code == 404, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # test for unexpected params and missing params
#    editor_obj, editor_obj, book_obj = _setup()
#    editor_dict = Genius.gen_editor_dict()
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/books/{book_obj.book_id}", json=editor_dict
#    )
#    assert response.status_code == 400, response.data


# Testing PATCH /editors/<id> endpoint
# def test_update_editor_by_id_endpoint(db_w_cleanup, staged_app_client): # 51/83
#    app, client = staged_app_client
#
#    # Testing base case
#    editor_obj = Genius.gen_editor_obj()
#    editor_dict = Genius.gen_editor_dict()
#    response = client.patch(f"/editors/{editor_obj.editor_id}", json=editor_dict)
#    DbBasedTester.test_editor_resp(response, editor_dict)
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 400 error if PATCHed json is empty
#    editor_obj = Genius.gen_editor_obj()
#    response = client.patch(f"/editors/{editor_obj.editor_id}", json={})
#    assert response.status_code == 400, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error if editor_id is bogus
#    bogus_editor_id = random.randint(1, 10)
#    editor_dict = Genius.gen_editor_dict()
#    response = client.patch(f"/editors/{bogus_editor_id}", json=editor_dict)
#    assert response.status_code == 404, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # test for unexpected params and missing params
#    editor_obj = Genius.gen_editor_obj()
#    book_dict = Genius.gen_book_dict()
#    response = client.patch(f"/editors/{editor_obj.editor_id}", json=book_dict)
#    assert response.status_code == 400, response.data


# Testing PATCH /editors/<id>/manuscripts/<id> endpoint
# def test_update_editor_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client): # 52/83
#    app, client = staged_app_client
#
#    def _setup():
#        editor_obj = Genius.gen_editor_obj()
#        editor_obj = Genius.gen_editor_obj()
#        manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
#        Genius.gen_editors_manuscripts_obj(
#            editor_obj.editor_id, manuscript_obj.manuscript_id
#        )
#        return editor_obj, editor_obj, manuscript_obj
#
#    # Testing base case
#    editor_obj, editor_obj, manuscript_obj = _setup()
#    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/manuscripts/{manuscript_obj.manuscript_id}",
#        json=manuscript_dict,
#    )
#    DbBasedTester.test_manuscript_resp(response, manuscript_dict)
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 400 error if PATCHed json is empty
#    editor_obj, editor_obj, manuscript_obj = _setup()
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/manuscripts/{manuscript_obj.manuscript_id}",
#        json={},
#    )
#    assert response.status_code == 400, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error if editor_id is bogus
#    editor_obj, editor_obj, manuscript_obj = _setup()
#    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
#    bogus_editor_id = randint_excluding(1, 10, editor_obj.editor_id)
#    assert editor_obj is not None
#    response = client.patch(
#        f"/editors/{bogus_editor_id}/manuscripts/{manuscript_obj.manuscript_id}",
#        json=manuscript_dict,
#    )
#    assert response.status_code == 404, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error if manuscript_id is bogus
#    editor_obj, editor_obj, manuscript_obj = _setup()
#    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
#    bogus_manuscript_id = randint_excluding(1, 10, manuscript_obj.manuscript_id)
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/manuscripts/{bogus_manuscript_id}",
#        json=manuscript_dict,
#    )
#    assert response.status_code == 404, response.data
#
#    DbBasedTester.cleanup__empty_all_tables()
#
#    # test for unexpected params and missing params
#    editor_obj, editor_obj, manuscript_obj = _setup()
#    editor_dict = Genius.gen_editor_dict()
#    response = client.patch(
#        f"/editors/{editor_obj.editor_id}/manuscripts/{manuscript_obj.manuscript_id}",
#        json=editor_dict,
#    )
#    assert response.status_code == 400, response.data
