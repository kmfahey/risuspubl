#!/usr/bin/python3

import os
import random

import faker
import pytest
from sqlalchemy.exc import LegacyAPIWarning
from risuspubl.dbmodels import Author, Editor, Book, Series


# Set environment variable for Flask's configuration
os.environ[
    "FLASK_ENV"
] = "testing"  # This should be set before creating the app instance.

faker_obj = faker.Faker()


def test_author_create_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    author_dict = dict(
        first_name=faker_obj.first_name(), last_name=faker_obj.last_name()
    )
    response = client.post("/authors", json=author_dict)
    assert response.status_code == 200
    author_objs = db.session.query(Author).all()
    assert len(author_objs) == 1
    assert author_objs[0].first_name == author_dict["first_name"]
    assert author_objs[0].last_name == author_dict["last_name"]


def test_create_author_book_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client

    def _setup():
        author_obj = Author(
            first_name=faker_obj.first_name(), last_name=faker_obj.last_name()
        )
        db.session.add(author_obj)
        editor_obj = Editor(
            first_name=faker_obj.first_name(),
            last_name=faker_obj.last_name(),
            salary=random.randint(65, 95) * 1000,
        )
        db.session.add(editor_obj)
        db.session.commit()

        book_dict = dict(
            title="The Accidental Wedding",
            publication_date=faker_obj.date_this_century().isoformat(),
            edition_number=random.randint(1, 5),
            is_in_print=bool(random.randint(0, 1)),
            editor_id=editor_obj.editor_id,
        )

        return author_obj.author_id, book_dict

    def _test(response, book_dict):
        assert response.status_code == 200
        resp_jsobj = response.get_json()
        assert resp_jsobj["edition_number"] == book_dict["edition_number"]
        assert resp_jsobj["editor_id"] == book_dict["editor_id"]
        assert resp_jsobj["is_in_print"] == book_dict["is_in_print"]
        assert resp_jsobj["publication_date"] == book_dict["publication_date"]
        assert resp_jsobj["title"] == book_dict["title"]
        return resp_jsobj

    author_id, book_dict = _setup()

    # Testing without series_id
    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj = _test(response, book_dict)
    assert resp_jsobj["series_id"] is None

    # Cleanup
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    # Testing with series_id
    author_id, book_dict = _setup()

    series_obj = Series(title="Sign of the Absent Puppet", volumes=random.randint(1, 5))
    db.session.add(series_obj)
    db.session.commit()
    book_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj = _test(response, book_dict)
    assert resp_jsobj["series_id"] == book_dict["series_id"], (resp_jsobj, book_dict)


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


def test_index_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    author_dicts = [
        dict(first_name=faker_obj.first_name(), last_name=faker_obj.last_name())
        for _ in range(10)
    ]
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


# def test_update_author_book_endpoint

# def test_update_author_by_id_endpoint

# def test_update_author_manuscript_endpoint

# def test_update_author_metadata_endpoint

# def test_update_authors_book_endpoint

# def test_update_authors_manuscript_endpoint
