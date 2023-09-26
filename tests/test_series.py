#!/usr/bin/python3

import os
import random
import pytest

from risuspubl.dbmodels import Series

from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing POST /series
def test_create_series_endpoint(db_w_cleanup, staged_app_client):  # 73/83
    app, client = staged_app_client

    # Testing base case
    series_dict = Genius.gen_series_dict()
    response = client.post("/series", json=series_dict)
    DbBasedTester.test_series_resp(response, series_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with missing or unexpected params
    # missing or unexpected params
    book_dict = Genius.gen_book_dict()
    response = client.post("/series", json=book_dict)
    assert response.status_code == 400, response.data.decode("utf8")


# Testing DELETE /series/<id> endpoint
def test_delete_series_by_id_endpoint(db_w_cleanup, staged_app_client):  # 74/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    series_obj = Genius.gen_series_obj()
    series_id = series_obj.series_id
    response = client.delete(f"/series/{series_id}")
    assert response.status_code == 200, response.data.decode("utf8")
    assert response.get_json() is True
    assert db.session.query(Series).get(series_id) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    bogus_series_id = random.randint(1, 10)
    response = client.delete(f"/series/{bogus_series_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /series/<id>/books/<id> endpoint
def test_display_series_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 75/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id, series_obj.series_id)
    response = client.get(f"/series/{series_obj.series_id}/books/{book_obj.book_id}")
    DbBasedTester.test_book_resp(response, book_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    bogus_series_id = random.randint(1, 10)
    response = client.get(f"/series/{bogus_series_id}/books/{book_obj.book_id}")
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the book_id is bogus
    series_obj = Genius.gen_series_obj()
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/series/{series_obj.series_id}/books/{bogus_book_id}")
    assert response.status_code == 404


# Testing GET /series/<id>/books endpoint
def test_display_series_books_endpoint(db_w_cleanup, staged_app_client):  # 76/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    book_objs_l = [
        Genius.gen_book_obj(editor_obj.editor_id, series_obj.series_id)
        for _ in range(3)
    ]
    response = client.get(f"/series/{series_obj.series_id}/books")
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

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    bogus_series_id = random.randint(1, 10)
    response = client.get(f"/series/{bogus_series_id}/books")
    assert response.status_code == 404


# Testing GET /series/<id> endpoint
def test_display_series_by_id_endpoint(db_w_cleanup, staged_app_client):  # 77/83
    app, client = staged_app_client

    # Testing base case
    series_obj = Genius.gen_series_obj()
    response = client.get(f"/series/{series_obj.series_id}")
    DbBasedTester.test_series_resp(response, series_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    bogus_series_id = random.randint(1, 10)
    response = client.get(f"/series/{bogus_series_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /series/<id>/manuscripts/<id> endpoint
def test_display_series_manuscript_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 78/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(
        editor_obj.editor_id, series_obj.series_id
    )
    response = client.get(
        f"/series/{series_obj.series_id}"
        + f"/manuscripts/{manuscript_obj.manuscript_id}"
    )
    DbBasedTester.test_manuscript_resp(response, manuscript_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    bogus_series_id = random.randint(1, 10)
    response = client.get(
        f"/series/{bogus_series_id}/manuscripts/{manuscript_obj.manuscript_id}"
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the manuscript_id is bogus
    series_obj = Genius.gen_series_obj()
    bogus_manuscript_id = random.randint(1, 10)
    response = client.get(
        f"/series/{series_obj.series_id}/manuscripts/{bogus_manuscript_id}"
    )
    assert response.status_code == 404


# Testing GET /series/<id>/manuscripts endpoint
def test_display_series_manuscripts_endpoint(db_w_cleanup, staged_app_client):  # 79/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_objs_l = [
        Genius.gen_manuscript_obj(editor_obj.editor_id, series_obj.series_id)
        for _ in range(3)
    ]
    response = client.get(f"/series/{series_obj.series_id}/manuscripts")
    assert response.status_code == 200, response.data.decode("utf8")
    for manuscript_jsobj in response.get_json():
        assert any(
            manuscript_jsobj["editor_id"] == manuscript_obj.editor_id
            and manuscript_jsobj["working_title"] == manuscript_obj.working_title
            and manuscript_jsobj["due_date"] == manuscript_obj.due_date.isoformat()
            and manuscript_jsobj["advance"] == manuscript_obj.advance
            for manuscript_obj in manuscript_objs_l
        )

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    bogus_series_id = random.randint(1, 10)
    response = client.get(f"/series/{bogus_series_id}/manuscripts")
    assert response.status_code == 404


# Testing GET /series
def test_index_endpoint(db_w_cleanup, staged_app_client):  # 80/83
    app, client = staged_app_client

    series_objs_l = [Genius.gen_series_obj() for _ in range(3)]
    response = client.get("/series")
    assert response.status_code == 200, response.data.decode("utf8")
    for series_jsobj in response.get_json():
        assert any(
            series_jsobj["title"] == series_obj.title
            and series_jsobj["volumes"] == series_obj.volumes
            for series_obj in series_objs_l
        )


# Testing PATCH /series/<id>/books/<id> endpoint
def test_update_series_book_by_id_endpoint(db_w_cleanup, staged_app_client):  # 81/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id, series_obj.series_id)
    new_book_dict = Genius.gen_book_dict(editor_obj.editor_id, series_obj.series_id)
    response = client.patch(
        f"/series/{series_obj.series_id}/books/{book_obj.book_id}", json=new_book_dict
    )
    DbBasedTester.test_book_resp(response, new_book_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    new_book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    bogus_series_id = random.randint(1, 10)
    response = client.patch(
        f"/series/{bogus_series_id}/books/{book_obj.book_id}", json=new_book_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the book_id is bogus
    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    book_dict = Genius.gen_book_dict(editor_obj.editor_id)
    bogus_book_id = random.randint(1, 10)
    response = client.patch(
        f"/series/{series_obj.series_id}/books/{bogus_book_id}", json=book_dict
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with missing or unexpected params
    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id, series_obj.series_id)
    author_dict = Genius.gen_author_dict()
    response = client.patch(
        f"/series/{series_obj.series_id}/books/{book_obj.book_id}", json=author_dict
    )
    assert response.status_code == 400, response.data.decode("utf8")


# Testing PATCH /series/<id> endpoint
def test_update_series_by_id_endpoint(db_w_cleanup, staged_app_client):  # 82/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    new_series_dict = Genius.gen_series_dict()
    response = client.patch(f"/series/{series_obj.series_id}", json=new_series_dict)
    DbBasedTester.test_series_resp(response, new_series_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    bogus_series_id = random.randint(1, 10)
    series_dict = Genius.gen_series_dict()
    response = client.patch(f"/series/{bogus_series_id}", json=series_dict)
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with missing or unexpected params
    series_obj = Genius.gen_series_obj()
    author_dict = Genius.gen_author_dict()
    response = client.patch(f"/series/{series_obj.series_id}", json=author_dict)
    assert response.status_code == 400, response.data.decode("utf8")


# Testing PATCH /series/<id>/manuscripts/<id> endpoint
def test_update_series_manuscript_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 83/83
    app, client = staged_app_client

    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(
        editor_obj.editor_id, series_obj.series_id
    )
    new_manuscript_dict = Genius.gen_manuscript_dict(
        editor_obj.editor_id, series_obj.series_id
    )
    response = client.patch(
        f"/series/{series_obj.series_id}/manuscripts/{manuscript_obj.manuscript_id}",
        json=new_manuscript_dict,
    )
    DbBasedTester.test_manuscript_resp(response, new_manuscript_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the series_id is bogus
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(editor_obj.editor_id)
    new_manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
    bogus_series_id = random.randint(1, 10)
    response = client.patch(
        f"/series/{bogus_series_id}/manuscripts/{manuscript_obj.manuscript_id}",
        json=new_manuscript_dict,
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when the manuscript_id is bogus
    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_dict = Genius.gen_manuscript_dict(editor_obj.editor_id)
    bogus_manuscript_id = random.randint(1, 10)
    response = client.patch(
        f"/series/{series_obj.series_id}/manuscripts/{bogus_manuscript_id}",
        json=manuscript_dict,
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with missing or unexpected params
    series_obj = Genius.gen_series_obj()
    editor_obj = Genius.gen_editor_obj()
    manuscript_obj = Genius.gen_manuscript_obj(
        editor_obj.editor_id, series_obj.series_id
    )
    author_dict = Genius.gen_author_dict()
    response = client.patch(
        f"/series/{series_obj.series_id}/manuscripts/{manuscript_obj.manuscript_id}",
        json=author_dict,
    )
    assert response.status_code == 400, response.data.decode("utf8")
