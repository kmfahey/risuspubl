#!/usr/bin/python3

import os
import random

import pprint
import json
import pytest
from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    AuthorsBooks,
    AuthorsManuscripts,
    Book,
    Manuscript,
)

from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


def test_delete_author_book_endpoint(db_w_cleanup, staged_app_client):  # 7/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    authors_books_obj = Genius.gen_authors_books_obj(author_obj.author_id, book_id)

    response = client.delete(f"/authors/{author_obj.author_id}/books/{book_id}")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is None
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_obj.author_id, book_id=book_id)
        .first()
        is None
    )

    DbBasedTester.cleanup__empty_all_tables()

    book_obj = Genius.gen_book_obj()
    bogus_author_id = random.randint(1, 10)
    response = client.delete(f"/authors/{bogus_author_id}/books/{book_obj.book_id}")
    assert response.status_code == 404
    assert db.session.query(Book).get(book_obj.book_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    author_obj = Genius.gen_author_obj()
    bogus_book_id = random.randint(1, 10)
    response = client.delete(f"/authors/{author_obj.author_id}/books/{bogus_book_id}")
    assert response.status_code == 404
    assert db.session.query(Author).get(author_obj.author_id) is not None


def test_delete_author_by_id_endpoint(db_w_cleanup, staged_app_client):  # 8/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id

    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id

    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id

    authors_books_obj = Genius.gen_authors_books_obj(
        author_obj.author_id, book_obj.book_id
    )
    authors_manuscripts_obj = Genius.gen_authors_manuscripts_obj(
        author_obj.author_id, manuscript_obj.manuscript_id
    )

    response = client.delete(f"/authors/{author_obj.author_id}")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Author).get(author_id) is None
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_id, book_id=book_id)
        .first()
    ) is None
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_id, manuscript_id=manuscript_id)
        .first()
    ) is None
    assert db.session.query(Book).get(book_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    bogus_author_id = random.randint(1, 10)
    response = client.delete(f"/authors/{bogus_author_id}")
    assert response.status_code == 404


def test_delete_author_manuscript_endpoint(db_w_cleanup, staged_app_client):  # 9/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    authors_manuscripts_obj = Genius.gen_authors_manuscripts_obj(
        author_obj.author_id, manuscript_id
    )

    response = client.delete(
        f"/authors/{author_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is None
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is None
    )

    DbBasedTester.cleanup__empty_all_tables()

    manuscript_obj = Genius.gen_manuscript_obj()
    bogus_author_id = random.randint(1, 10)
    response = client.delete(
        f"/authors/{bogus_author_id}/manuscripts/{manuscript_obj.manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Manuscript).get(manuscript_obj.manuscript_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    author_obj = Genius.gen_author_obj()
    bogus_manuscript_id = random.randint(1, 10)
    response = client.delete(
        f"/authors/{author_obj.author_id}/manuscripts/{bogus_manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Author).get(author_obj.author_id) is not None


def test_delete_author_metadata_endpoint(db_w_cleanup, staged_app_client):  # 10/83
    db = db_w_cleanup
    app, client = staged_app_client
#
    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    metadata_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
    response = client.delete(f"/authors/{author_id}/metadata")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert (
        db.session.query(AuthorMetadata)
        .filter_by(author_id=author_id)
        .first()
    ) is None
    assert db.session.query(Author).get(author_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    response = client.delete(f"/authors/{author_id}/metadata")
    assert response.status_code == 404
    assert db.session.query(Author).get(author_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    metadata_no1_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
    metadata_no2_obj = Genius.gen_author_metadata_obj(author_obj.author_id)
    metadata_no1_id = metadata_no1_obj.author_metadata_id
    metadata_no2_id = metadata_no2_obj.author_metadata_id
    response = client.delete(f"/authors/{author_id}/metadata")
    assert response.status_code == 500
    assert db.session.query(Author).get(author_id) is not None
    assert db.session.query(AuthorMetadata).get(metadata_no1_id) is not None
    assert db.session.query(AuthorMetadata).get(metadata_no2_id) is not None


# def test_delete_authors_book_endpoint # 11/83

# def test_delete_authors_manuscript_endpoint # 12/83
