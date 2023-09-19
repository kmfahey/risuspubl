#!/usr/bin/python3

import os
import random
import math
from datetime import date

import pprint
import json
import faker
import pytest
from risuspubl.dbmodels import Author, AuthorMetadata, Book, Editor, Manuscript, Series


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# called it Genius because Generator already has a definition in python.
class Genius:
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

    hexdigit_cp = tuple(range(48, 58)) + tuple(range(97, 103))

    def __init__(self, db):
        self.db = db

    @classmethod
    def gen_author_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(), last_name=cls.faker_obj.last_name()
        )

    @classmethod
    def gen_author_metadata_dict(cls, author_id=None):
        photo_res_horiz = random.randint(200, 1000)
        photo_res_vert = math.floor(photo_res_horiz * 1.5)
        retdict = dict(
            age=random.randint(18, 75),
            biography=cls.lorem_ipsum,
            photo_url=f"https://risuspublishing.com/cms/img/{cls.gen_hexdigits(16)}.jpeg",
            photo_res_horiz=photo_res_horiz,
            photo_res_vert=photo_res_vert,
        )
        if author_id is not None:
            retdict["author_id"] = author_id
        return retdict

    @classmethod
    def gen_book_dict(cls, editor_id=None, series_id=None):
        retdict = dict(
            edition_number=random.randint(1, 5),
            is_in_print=bool(random.randint(0, 1)),
            publication_date=cls.faker_obj.date_this_century().isoformat(),
            title=random.choice(cls.book_titles),
        )
        if editor_id is not None:
            retdict["editor_id"] = editor_id
        if series_id is not None:
            retdict["series_id"] = series_id
        return retdict

    @classmethod
    def gen_editor_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(),
            last_name=cls.faker_obj.last_name(),
            salary=random.randint(65, 95) * 1000,
        )

    @classmethod
    def gen_hexdigits(cls, number_of_chars):
        return "".join(
            chr(random.choice(cls.hexdigit_cp)) for _ in range(number_of_chars)
        )

    @classmethod
    def gen_manuscript_dict(cls, editor_id=None, series_id=None):
        retdict = dict(
            advance=random.randint(10, 20) * 1000,
            due_date=cls.faker_obj.date_between_dates(
                date.today(), date(date.today().year + 2, date.today().month, 1)
            ).isoformat(),
            series_id=None,
            working_title=random.choice(cls.manuscript_titles),
        )
        if editor_id is not None:
            retdict["editor_id"] = editor_id
        if series_id is not None:
            retdict["series_id"] = series_id
        return retdict

    @classmethod
    def gen_series_dict(cls):
        return dict(
            title=random.choice(cls.series_titles), volumes=random.randint(1, 5)
        )

    def gen_author_metadata_obj(self, author_obj):
        author_metadata_obj = AuthorMetadata(
            **self.gen_author_metadata_dict(author_obj)
        )
        self.db.session.add(author_metadata_obj)
        self.db.session.commit()
        return author_metadata_obj

    def gen_author_obj(self):
        author_obj = Author(**self.gen_author_dict())
        self.db.session.add(author_obj)
        self.db.session.commit()
        return author_obj

    def gen_editor_obj(self):
        editor_obj = Editor(**self.gen_editor_dict())
        self.db.session.add(editor_obj)
        self.db.session.commit()
        return editor_obj

    def gen_manuscript_obj(self, editor_id=None):
        manuscript_obj = Manuscript(**self.gen_manuscript_dict(editor_obj.editor_id))
        self.db.session.add(manuscript_obj)
        self.db.session.commit()
        return manuscript_obj

    def gen_series_obj(self):
        series_obj = Series(**self.gen_series_dict())
        self.db.session.add(series_obj)
        self.db.session.commit()
        return series_obj


def _test_book_resp(response, book_dict):
    assert response.status_code == 200, response.data
    resp_jsobj = response.get_json()
    assert resp_jsobj["edition_number"] == book_dict["edition_number"]
    assert resp_jsobj["editor_id"] == book_dict["editor_id"]
    assert resp_jsobj["is_in_print"] == book_dict["is_in_print"]
    assert resp_jsobj["publication_date"] == book_dict["publication_date"]
    assert resp_jsobj["title"] == book_dict["title"]
    return resp_jsobj


def _cleanup__empty_all_tables(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


def test_author_create_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    genius = Genius(db)

    author_dict = genius.gen_author_dict()
    response = client.post("/authors", json=author_dict)
    assert response.status_code == 200
    author_objs = db.session.query(Author).all()
    assert len(author_objs) == 1
    assert author_objs[0].first_name == author_dict["first_name"]
    assert author_objs[0].last_name == author_dict["last_name"]


def test_create_author_book_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    genius = Genius(db)

    def _setup():
        author_obj = genius.gen_author_obj()
        editor_obj = genius.gen_editor_obj()

        book_dict = genius.gen_book_dict(editor_obj.editor_id)

        return author_obj.author_id, book_dict

    author_id, book_dict = _setup()

    # Testing without series_id
    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj = _test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] is None

    _cleanup__empty_all_tables(db)

    # Testing with series_id
    author_id, book_dict = _setup()

    series_obj = genius.gen_series_obj()
    book_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    resp_jsobj = _test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] == book_dict["series_id"], (resp_jsobj, book_dict)

    _cleanup__empty_all_tables(db)

    # Testing with bogus id
    bogus_author_id = random.randint(1, 10)
    response = client.post("f/authors/{bogus_author_id}/", json=book_dict)
    assert response.status_code == 404

    _cleanup__empty_all_tables(db)

    # Testing with including author_id in POSTed json
    author_id, book_dict = _setup()

    book_dict["author_id"] = author_id

    response = client.post(f"/authors/{author_id}/books", json=book_dict)
    assert response.status_code == 400


def test_create_author_manuscript_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    genius = Genius(db)

    def _setup():
        author_obj = genius.gen_author_obj()
        editor_obj = genius.gen_editor_obj()

        manuscript_dict = genius.gen_manuscript_dict(editor_obj.editor_id)

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

    _cleanup__empty_all_tables(db)

    # Testing with series_id
    author_id, manuscript_dict = _setup()

    series_obj = genius.gen_series_obj()
    manuscript_dict["series_id"] = series_obj.series_id

    response = client.post(f"/authors/{author_id}/manuscripts", json=manuscript_dict)
    resp_jsobj = _test(response, manuscript_dict)
    assert resp_jsobj["series_id"] == manuscript_dict["series_id"], (
        resp_jsobj,
        manuscript_dict,
    )

    _cleanup__empty_all_tables(db)

    bogus_author_id = random.randint(1, 10)
    response = client.post("f/authors/{bogus_author_id}/", json=manuscript_dict)
    assert response.status_code == 404


def test_create_author_metadata_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    genius = Genius(db)

    author_obj = genius.gen_author_obj()
    metadata_dict = genius.gen_author_metadata_dict()

    response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )

    resp_jsobj = response.get_json()
    assert response.status_code == 200
    assert resp_jsobj["age"] == metadata_dict["age"]
    assert resp_jsobj["author_id"] == author_obj.author_id
    assert resp_jsobj["biography"] == metadata_dict["biography"]
    assert resp_jsobj["photo_res_horiz"] == metadata_dict["photo_res_horiz"]
    assert resp_jsobj["photo_res_vert"] == metadata_dict["photo_res_vert"]
    assert resp_jsobj["photo_url"] == metadata_dict["photo_url"]

    other_metadata_dict = genius.gen_author_metadata_dict(author_obj.author_id)

    other_response = client.post(
        f"/authors/{author_obj.author_id}/metadata", json=metadata_dict
    )

    assert other_response.status_code == 400

    # Done this way to ensure it isn't accidentally equal to author_obj.author_id
    bogus_author_id = random.choice(
        range(author_obj.author_id + 1, author_obj.author_id + 10)
    )

    failed_response = client.post(
        f"/authors/{bogus_author_id}/metadata", json=metadata_dict
    )

    assert failed_response.status_code == 404


def test_create_authors_book_endpoint(fresh_tables_db, staged_app_client):
    db = fresh_tables_db
    app, client = staged_app_client
    genius = Genius(db)

    def _setup(w_series_id=False):
        author_obj_no1 = genius.gen_author_obj()
        author_obj_no2 = genius.gen_author_obj()
        editor_obj = genius.gen_editor_obj()

        if w_series_id:
            series_obj = genius.gen_series_obj()
            book_dict = genius.gen_book_dict(editor_obj.editor_id, series_obj.series_id)
        else:
            book_dict = genius.gen_book_dict(editor_obj.editor_id)

        return author_obj_no1.author_id, author_obj_no2.author_id, book_dict

    # Testing without series id

    author_no1_id, author_no2_id, book_dict = _setup()
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    resp_jsobj = _test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] is None
    _cleanup__empty_all_tables(db)

    # Testing with series id
    author_no1_id, author_no2_id, book_dict = _setup(w_series_id=True)
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    resp_jsobj = _test_book_resp(response, book_dict)
    assert resp_jsobj["series_id"] == book_dict["series_id"]

    _cleanup__empty_all_tables(db)

    # Testing with bogus author_id, first position
    author_id, _, book_dict = _setup()
    bogus_author_id = random.choice(range(author_id + 1, author_id + 10))
    response = client.post(
        f"/authors/{author_id}/{bogus_author_id}/books", json=book_dict
    )
    assert response.status_code == 404

    _cleanup__empty_all_tables(db)

    # Testing with bogus author_id, second position
    author_id, _, book_dict = _setup()
    bogus_author_id = random.choice(range(author_id + 1, author_id + 10))
    response = client.post(
        f"/authors/{bogus_author_id}/{author_id}/books", json=book_dict
    )
    assert response.status_code == 404

    _cleanup__empty_all_tables(db)

    # Testing with unexpected property
    author_no1_id, author_no2_id, book_dict = _setup()
    book_dict["unexpected_prop"] = True
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data

    _cleanup__empty_all_tables(db)

    # Testing with missing property
    author_no1_id, author_no2_id, book_dict = _setup()
    del book_dict["title"]
    response = client.post(
        f"/authors/{author_no1_id}/{author_no2_id}/books", json=book_dict
    )
    assert response.status_code == 400, response.data


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
    genius = Genius(db)

    author_dicts = [genius.gen_author_dict() for _ in range(10)]
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
