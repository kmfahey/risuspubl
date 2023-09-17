#!/usr/bin/python3

import os
import random
import math
from datetime import date

import faker
import pytest
from risuspubl.dbmodels import Author, AuthorMetadata, Book, Editor, Manuscript, Series


# Set environment variable for Flask's configuration
os.environ[
    "FLASK_ENV"
] = "testing"  # This should be set before creating the app instance.


class Generate:
    lorem_ipsum = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor \
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis \
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. \
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore \
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt \
in culpa qui officia deserunt mollit anim id est laborum."""

    faker_obj = faker.Faker()

    book_titles = [
        "Steel Alley",
        "The Blessed Beast",
        "Death of the Stuffed Viper",
        "Death of the Filthy Beast",
        "Crime of the Voiceless Mermaid",
        "Clue of the Cold Puppet",
        "Angel's Return",
        "Death of the Fake Pygmy",
        "Elysium Crying",
        "Alpha Grieving",
    ]

    manuscript_titles = [
        "The Dynasty of Legend",
        "Case of the Giant Lynx",
        "The Burden of the Exiled",
        "The Widow in the Portrait",
        "2132: Rigel",
        "Copper Heart",
        "The Brute in the West",
        "Darling Dearest",
        "Prophecy Returning",
        "Case of the Stuffed Shih Tzu",
    ]

    series_titles = [
        "The Owl in the Air",
        "Sign of the Hollow Staircase",
        "Fatal Demon",
        "Crime of the Orange Tourists",
        "Sign of the Absent Puppet",
        "Khan's Vow",
        "Made for Duty",
        "The Scarlet Violin",
        "Mister Silver Fox",
        "Legacy Fading",
    ]

    def __init__(self, db):
        self.db = db

    @classmethod
    def author_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(), last_name=cls.faker_obj.last_name()
        )

    @classmethod
    def author_metadata_dict(cls, author_obj):
        photo_res_horiz = random.randint(200, 1000)
        photo_res_vert = math.floor(photo_res_horiz * 1.5)
        return dict(
            age=random.randint(18, 75),
            author_id=author_obj.author_id,
            biography=cls.lorem_ipsum,
            photo_url=f"https://risuspublishing.com/cms/img/{cls.hexdigits(16)}.jpeg",
            photo_res_horiz=photo_res_horiz,
            photo_res_vert=photo_res_vert,
        )

    @classmethod
    def book_dict(cls, editor_obj):
        return dict(
            edition_number=random.randint(1, 5),
            editor_id=editor_obj.editor_id,
            is_in_print=bool(random.randint(0, 1)),
            publication_date=cls.faker_obj.date_this_century().isoformat(),
            title=random.choice(cls.book_titles),
        )

    @classmethod
    def editor_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(),
            last_name=cls.faker_obj.last_name(),
            salary=random.randint(65, 95) * 1000,
        )

    @classmethod
    def hexdigits(cls, number_of_chars):
        return "".join(
            chr(random.choice(cls.hexdigit_codepts) for _ in range(number_of_chars))
        )

    @classmethod
    def manuscript_dict(cls, editor_obj):
        return dict(
            advance=random.randint(10, 20) * 1000,
            due_date=cls.faker_obj.date_between_dates(
                date.today(), date(date.today().year + 2, date.today().month, 1)
            ).isoformat(),
            editor_id=editor_obj.editor_id,
            series_id=None,
            working_title=random.choice(cls.manuscript_titles),
        )

    @classmethod
    def series_dict(cls):
        return dict(
            title=random.choice(cls.series_titles), volumes=random.randint(1, 5)
        )

    def author_metadata_obj(self, author_obj):
        author_metadata_obj = AuthorMetadata(**self.author_metadata_dict(author_obj))
        self.db.session.add(author_metadata_obj)
        self.db.session.commit()
        return author_metadata_obj

    def author_obj(self):
        author_obj = Author(**self.author_dict())
        self.db.session.add(author_obj)
        self.db.session.commit()
        return author_obj

    def editor_obj(self):
        editor_obj = Editor(**self.editor_dict())
        self.db.session.add(editor_obj)
        self.db.session.commit()
        return editor_obj

    def manuscript_obj(self, editor_obj):
        manuscript_obj = Manuscript(**self.manuscript_dict(editor_obj))
        self.db.session.add(manuscript_obj)
        self.db.session.commit()
        return manuscript_obj

    def series_obj(self):
        series_obj = Series(**self.series_dict())
        self.db.session.add(series_obj)
        self.db.session.commit()
        return series_obj


def test_author_create_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    generate = Generate(db)

    author_dict = generate.author_dict()
    response = client.post("/authors", json=author_dict)
    assert response.status_code == 200
    author_objs = db.session.query(Author).all()
    assert len(author_objs) == 1
    assert author_objs[0].first_name == author_dict["first_name"]
    assert author_objs[0].last_name == author_dict["last_name"]


def test_create_author_book_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    generate = Generate(db)

    def _setup():
        author_obj = generate.author_obj()
        editor_obj = generate.editor_obj()

        book_dict = generate.book_dict(editor_obj)

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

    series_obj = generate.series_obj()
    book_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj = _test(response, book_dict)
    assert resp_jsobj["series_id"] == book_dict["series_id"], (resp_jsobj, book_dict)

    # Cleanup
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    bogus_author_id = random.randint(1, 10)
    response = client.post("f/authors/{bogus_author_id}/", json=book_dict)
    assert response.status_code == 404


def test_create_author_manuscript_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    generate = Generate(db)

    def _setup():
        author_obj = generate.author_obj()
        editor_obj = generate.editor_obj()

        manuscript_dict = generate.manuscript_dict(editor_obj)

        return author_obj.author_id, manuscript_dict

    def _test(response, manuscript_dict):
        assert response.status_code == 200
        resp_jsobj = response.get_json()
        assert resp_jsobj["editor_id"] == manuscript_dict["editor_id"]
        assert resp_jsobj["working_title"] == manuscript_dict["working_title"]
        assert resp_jsobj["due_date"] == manuscript_dict["due_date"]
        assert resp_jsobj["advance"] == manuscript_dict["advance"]
        return resp_jsobj

    author_id, manuscript_dict = _setup()

    # Testing without series_id
    response = client.post(f"/authors/{author_id}/manuscripts", json=manuscript_dict)
    resp_jsobj = _test(response, manuscript_dict)
    assert resp_jsobj["series_id"] is None

    # Cleanup
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    # Testing with series_id
    author_id, manuscript_dict = _setup()

    series_obj = generate.series_obj()
    manuscript_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/manuscripts", json=manuscript_dict)
    resp_jsobj = _test(response, manuscript_dict)
    assert resp_jsobj["series_id"] == manuscript_dict["series_id"], (
        resp_jsobj,
        manuscript_dict,
    )

    # Cleanup
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    bogus_author_id = random.randint(1, 10)
    response = client.post("f/authors/{bogus_author_id}/", json=manuscript_dict)
    assert response.status_code == 404


def test_create_author_metadata_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    generate = Generate(db)


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
    generate = Generate(db)

    author_dicts = [generate.author_dict() for _ in range(10)]
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
