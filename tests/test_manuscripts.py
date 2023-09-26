#!/usr/bin/python3

import os
import random
import pprint
import json

import pytest

from risuspubl.dbmodels import (
    Author,
    AuthorsManuscripts,
    Manuscript,
)
from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing DELETE /manuscripts/<id>
def test_delete_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client):  # 53/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_id, manuscript_id)
    response = client.delete(f"/manuscripts/{manuscript_id}")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Author).get(author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is None
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_id, manuscript_id=manuscript_id)
        .first()
    ) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus manuscript_id
    bogus_manuscript_id = random.randint(1, 10)
    response = client.delete(f"/manuscripts/{bogus_manuscript_id}")
    assert response.status_code == 404, response.data


# Testing the GET /manuscripts/<id> endpoint
def test_display_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client):  # 54/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    response = client.get(f"/manuscripts/{manuscript_obj.manuscript_id}")
    DbBasedTester.test_manuscript_resp(response, manuscript_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus manuscript_id
    bogus_manuscript_id = random.randint(1, 10)
    response = client.get(f"/manuscripts/{bogus_manuscript_id}")
    assert response.status_code == 404, response.data


#  Testing the GET /manuscripts endpoint
def test_index_endpoint(db_w_cleanup, staged_app_client):  # 55/83
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_objs_l = list()
    for _ in range(3):
        manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
        manuscript_objs_l.append(manuscript_obj)
        Genius.gen_authors_manuscripts_obj(
            author_obj.author_id, manuscript_obj.manuscript_id
        )
    response = client.get("/manuscripts")
    assert response.status_code == 200
    for manuscript_jsobj in response.get_json():
        assert any(
            manuscript_jsobj["editor_id"] == manuscript_obj.editor_id
            and manuscript_jsobj["working_title"] == manuscript_obj.working_title
            and manuscript_jsobj["due_date"] == manuscript_obj.due_date.isoformat()
            and manuscript_jsobj["advance"] == manuscript_obj.advance
            for manuscript_obj in manuscript_objs_l
        )


# Testing the PATCH /manuscripts/<id> endpoint
def test_update_manuscript_by_id_endpoint(db_w_cleanup, staged_app_client):  # 56/83
    app, client = staged_app_client

    # Testing base case
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
    response = client.patch(
        f"/manuscripts/{manuscript_obj.manuscript_id}", json=manuscript_dict
    )
    DbBasedTester.test_manuscript_resp(response, manuscript_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
    response = client.patch(f"/manuscripts/{manuscript_obj.manuscript_id}", json={})
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if manuscript_id is bogus
    bogus_manuscript_id = random.randint(1, 10)
    manuscript_dict = Genius.gen_manuscript_dict()
    response = client.patch(f"/manuscripts/{bogus_manuscript_id}", json=manuscript_dict)
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    author_dict = Genius.gen_author_dict()
    response = client.patch(
        f"/manuscripts/{manuscript_obj.manuscript_id}", json=author_dict
    )
    assert response.status_code == 400, response.data
