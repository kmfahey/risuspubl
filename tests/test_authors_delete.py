#!/usr/bin/python3

import os
import random

import json
from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    AuthorsBooks,
    AuthorsManuscripts,
    Book,
    Manuscript,
)

from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the DELETE /authors/<id>/books/<id> endpoint -- test 7 of 84
def test_delete_author_book_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_obj.author_id, book_id)

    response = client.delete(f"/authors/{author_obj.author_id}/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json() is True
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


# Testing the DELETE /authors/<id> endpoint -- test 8 of 84
def test_delete_author_by_id_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id

    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id

    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id

    Genius.gen_authors_books_obj(author_obj.author_id, book_obj.book_id)
    Genius.gen_authors_manuscripts_obj(
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


# Testing the DELETE /authors/<id>/manuscripts/<id> endpoint -- test 9 of 84
def test_delete_author_manuscript_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    author_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_obj.author_id, manuscript_id)

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


# Testing the DELETE /authors/<id>/metadata endpoint -- test 10 of 84
def test_delete_author_metadata_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client
    #
    author_obj = Genius.gen_author_obj()
    author_id = author_obj.author_id
    Genius.gen_metadata_obj(author_obj.author_id)
    response = client.delete(f"/authors/{author_id}/metadata")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert (
        db.session.query(AuthorMetadata).filter_by(author_id=author_id).first()
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
    metadata_no1_obj = Genius.gen_metadata_obj(author_obj.author_id)
    metadata_no2_obj = Genius.gen_metadata_obj(author_obj.author_id)
    metadata_no1_id = metadata_no1_obj.author_metadata_id
    metadata_no2_id = metadata_no2_obj.author_metadata_id
    response = client.delete(f"/authors/{author_id}/metadata")
    assert response.status_code == 500
    assert db.session.query(Author).get(author_id) is not None
    assert db.session.query(AuthorMetadata).get(metadata_no1_id) is not None
    assert db.session.query(AuthorMetadata).get(metadata_no2_id) is not None


# Testing the DELETE /authors/<id>/<id>/books/<id> endpoint -- test 11 of 84
def test_delete_authors_book_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # 1.
    # Testing base case where book object is deleted, likewise both
    # authors_books objects.
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_no1_obj.author_id, book_id)
    Genius.gen_authors_books_obj(author_no2_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 200
    assert json.loads(response.data) is True
    # Testing that both rows in the authors table are still there, and
    # the books row is gone
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is None
    # Confirming that the authors_books rows are gone.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no1_obj.author_id, book_id=book_id)
        .first()
        is None
    )
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no2_obj.author_id, book_id=book_id)
        .first()
        is None
    )

    DbBasedTester.cleanup__empty_all_tables()

    # 2.
    # Testing whether RPC fails when the first author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{author_obj.author_id}/{bogus_author_id}/books/{book_id}"
    )
    assert response.status_code == 404
    # Testing that the authors table row and the books table row are
    # both still present
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is not None
    # Confirming that the authors_books row *isn't* gone.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_obj.author_id, book_id=book_id)
        .first()
        is not None
    )

    DbBasedTester.cleanup__empty_all_tables()

    # 3.
    # Testing whether RPC fails when the *second* author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_obj.author_id, book_id)

    response = client.delete(
        f"/authors/{bogus_author_id}/{author_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 404
    # Testing that the authors table row and the books table row are
    # both still present
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is not None
    # Confirming that the authors_books row *isn't* gone.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_obj.author_id, book_id=book_id)
        .first()
        is not None
    )

    # 4.
    # Testing whether RPC fails when the *second* author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{bogus_author_id}/{author_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 404
    # Testing that the authors table row and the books table row are
    # both still present
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is not None
    # Confirming that the authors_books row *isn't* gone.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_obj.author_id, book_id=book_id)
        .first()
        is not None
    )

    # 5.
    # Testing whether RPC fails when the book_id is bogus.
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    bogus_book_id = random.randint(1, 10)

    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{bogus_book_id}"
    )
    assert response.status_code == 404
    # Testing that both authors table rows are both still present
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None

    # 6.
    # Testing whether RPC fails when the authors_books row for the first
    # authors row mentioned isn't present
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_no1_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 404
    # Testing that both authors table rows and the books table row are
    # still present
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is not None
    # Confirming that the one authors_books row is still present.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no1_obj.author_id, book_id=book_id)
        .first()
        is not None
    )

    # 7.
    # Testing whether RPC fails when the authors_books row for the
    # *second* authors row mentioned isn't present
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_no2_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 404
    # Testing that both authors table rows and the books table row are
    # still present
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Book).get(book_id) is not None
    # Confirming that the one authors_books row is still present.
    assert (
        db.session.query(AuthorsBooks)
        .filter_by(author_id=author_no2_obj.author_id, book_id=book_id)
        .first()
        is not None
    )

    # Testing for 400 error when author_id arguments are equal
    author_obj = Genius.gen_author_obj()
    book_obj = Genius.gen_book_obj()
    book_id = book_obj.book_id
    Genius.gen_authors_books_obj(author_obj.author_id, book_id)
    response = client.delete(
        f"/authors/{author_obj.author_id}" + f"/{author_obj.author_id}/books/{book_id}"
    )
    assert response.status_code == 400


# Testing the DELETE /authors/<id>/<id>/manuscripts/<id> endpoint -- test 12 of 84
def test_delete_authors_manuscript_endpoint(db_w_cleanup, staged_app_client):
    db = db_w_cleanup
    app, client = staged_app_client

    # 1.
    # Testing base case where manuscript object is deleted, likewise both
    # authors_manuscripts objects.
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_no1_obj.author_id, manuscript_id)
    Genius.gen_authors_manuscripts_obj(author_no2_obj.author_id, manuscript_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is None
    # Confirming that the authors_manuscripts rows are gone.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no1_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is None
    )
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no2_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is None
    )

    DbBasedTester.cleanup__empty_all_tables()

    # 2.
    # Testing whether RPC fails when the first author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_obj.author_id, manuscript_id)

    response = client.delete(
        f"/authors/{author_obj.author_id}/{bogus_author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None
    # Confirming that the authors_manuscripts row *isn't* gone.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is not None
    )

    DbBasedTester.cleanup__empty_all_tables()

    # 3.
    # Testing whether RPC fails when the *second* author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_obj.author_id, manuscript_id)

    response = client.delete(
        f"/authors/{bogus_author_id}/{author_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None
    # Confirming that the authors_manuscripts row *isn't* gone.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is not None
    )

    # 4.
    # Testing whether RPC fails when the *second* author_id is bogus.
    author_obj = Genius.gen_author_obj()
    bogus_author_id = randint_excluding(1, 10, author_obj.author_id)
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_obj.author_id, manuscript_id)

    response = client.delete(
        f"/authors/{bogus_author_id}/{author_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Author).get(author_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None
    # Confirming that the authors_manuscripts row *isn't* gone.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is not None
    )

    # 5.
    # Testing whether RPC fails when the manuscript_id is bogus.
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    bogus_manuscript_id = random.randint(1, 10)

    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/manuscripts/{bogus_manuscript_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None

    # 6.
    # Testing whether RPC fails when the authors_manuscripts row for the first
    # authors row mentioned isn't present
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_no1_obj.author_id, manuscript_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 404
    # Testing that both authors table rows and the manuscripts table row are
    # still present
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None
    # Confirming that the one authors_manuscripts row is still present.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no1_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is not None
    )

    # 7.
    # Testing whether RPC fails when the authors_manuscripts row for the
    # *second* authors row mentioned isn't present
    author_no1_obj = Genius.gen_author_obj()
    author_no2_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_no2_obj.author_id, manuscript_id)
    response = client.delete(
        f"/authors/{author_no1_obj.author_id}"
        + f"/{author_no2_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 404
    # Testing that both authors table rows and the manuscripts table row are
    # still present
    assert db.session.query(Author).get(author_no1_obj.author_id) is not None
    assert db.session.query(Author).get(author_no2_obj.author_id) is not None
    assert db.session.query(Manuscript).get(manuscript_id) is not None
    # Confirming that the one authors_manuscripts row is still present.
    assert (
        db.session.query(AuthorsManuscripts)
        .filter_by(author_id=author_no2_obj.author_id, manuscript_id=manuscript_id)
        .first()
        is not None
    )

    # Testing for 400 error when author_id arguments are equal
    author_obj = Genius.gen_author_obj()
    manuscript_obj = Genius.gen_manuscript_obj()
    manuscript_id = manuscript_obj.manuscript_id
    Genius.gen_authors_manuscripts_obj(author_obj.author_id, manuscript_id)
    response = client.delete(
        f"/authors/{author_obj.author_id}"
        + f"/{author_obj.author_id}/manuscripts/{manuscript_id}"
    )
    assert response.status_code == 400
