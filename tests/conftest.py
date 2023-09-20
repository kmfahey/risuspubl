#!/usr/bin/python3

import math
import os
import random
from datetime import date

import faker
import pytest
import psycopg2

from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    Book,
    Editor,
    Manuscript,
    Series,
    db,
)
from risuspubl.flaskapp import create_app


# Set environment variable for Flask's configuration
os.environ[
    "FLASK_ENV"
] = "testing"  # This should be set before creating the app instance.


def pytest_sessionstart(session):
    # PostgreSQL server details
    HOST = "localhost"
    PORT = 5432
    TARGET_DATABASE = "risusp_test"
    TARGET_USER = "pguser"
    TARGET_PASSWORD = "pguser"  # Be careful with storing plaintext passwords!

    # Check for user existence by attempting to connect with the provided credentials
    try:
        # This connection will just use the default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=TARGET_USER,
            password=TARGET_PASSWORD,
            host=HOST,
            port=PORT,
        )
    except psycopg2.OperationalError as e:
        if (
            "password authentication failed" in str(e)
            or "role" in str(e)
            and "does not exist" in str(e)
        ):
            pytest.exit(
                f"The user '{TARGET_USER}' does not exist or wrong password "
                + "provided. Please run ansible with setup_playbook.yml."
            )
        pytest.exit(f"Failed to connect to the PostgreSQL server. Error: {str(e)}")

    # If the above connection succeeded, the user exists. Now, check for the database's existence.
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM pg_database WHERE datname='{TARGET_DATABASE}'"
            )
            if not cursor.fetchone():
                pytest.exit(
                    f"The test database '{TARGET_DATABASE}' does not exist. "
                    + "Please run ansible with setup_playbook.yml."
                )
    finally:
        conn.close()


@pytest.fixture
def db_w_cleanup():
    yield db

    DbBasedTester.cleanup__empty_all_tables()


@pytest.fixture(scope="session")
def staged_app_client():
    # Create the Flask app instance using the test config
    app = create_app(
        dict(
            SQLALCHEMY_DATABASE_URI="postgresql://pguser:pguser@localhost:5432/risusp_test"
        )
    )
    app_context = app.app_context()
    app_context.push()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield app, client

        db.session.commit()
        db.session.close()

        db.drop_all()


__all__ = "Genius", "DbBasedTester"


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

    @classmethod
    def gen_author_metadata_obj(cls, author_obj):
        author_metadata_obj = AuthorMetadata(**cls.gen_author_metadata_dict(author_obj))
        db.session.add(author_metadata_obj)
        db.session.commit()
        return author_metadata_obj

    @classmethod
    def gen_author_obj(cls):
        author_obj = Author(**cls.gen_author_dict())
        db.session.add(author_obj)
        db.session.commit()
        return author_obj

    @classmethod
    def gen_editor_obj(cls):
        editor_obj = Editor(**cls.gen_editor_dict())
        db.session.add(editor_obj)
        db.session.commit()
        return editor_obj

    @classmethod
    def gen_manuscript_obj(cls, editor_id=None):
        manuscript_obj = Manuscript(**cls.gen_manuscript_dict(editor_id))
        db.session.add(manuscript_obj)
        db.session.commit()
        return manuscript_obj

    @classmethod
    def gen_series_obj(cls):
        series_obj = Series(**cls.gen_series_dict())
        db.session.add(series_obj)
        db.session.commit()
        return series_obj


class DbBasedTester:
    __slots__ = ("db",)

    @classmethod
    def test_book_resp(cls, response, book_dict):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        assert book_dict["edition_number"] == resp_jsobj["edition_number"]
        assert book_dict["editor_id"] == resp_jsobj["editor_id"]
        assert book_dict["is_in_print"] == resp_jsobj["is_in_print"]
        assert book_dict["publication_date"] == resp_jsobj["publication_date"]
        assert book_dict["title"] == resp_jsobj["title"]

        book_obj = db.session.query(Book).get(resp_jsobj["book_id"])
        assert book_dict["edition_number"] == book_obj.edition_number
        assert book_dict["editor_id"] == book_obj.editor_id
        assert book_dict["is_in_print"] == book_obj.is_in_print
        assert book_dict["publication_date"] == book_obj.publication_date.isoformat()
        assert book_dict["title"] == book_obj.title

        return resp_jsobj, book_obj

    @classmethod
    def test_manuscript_resp(cls, response, manuscript_dict):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        assert manuscript_dict["editor_id"] == resp_jsobj["editor_id"]
        assert manuscript_dict["working_title"] == resp_jsobj["working_title"]
        assert manuscript_dict["due_date"] == resp_jsobj["due_date"]
        assert manuscript_dict["advance"] == resp_jsobj["advance"]

        manuscript_obj = db.session.query(Manuscript).get(resp_jsobj["manuscript_id"])
        assert manuscript_dict["editor_id"] == manuscript_obj.editor_id
        assert manuscript_dict["working_title"] == manuscript_obj.working_title
        assert manuscript_dict["due_date"] == manuscript_obj.due_date.isoformat()
        assert manuscript_dict["advance"] == manuscript_obj.advance

        return resp_jsobj, manuscript_obj

    @classmethod
    def test_metadata_resp(cls, response, metadata_dict):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        assert metadata_dict["age"] == resp_jsobj["age"]
        assert metadata_dict["biography"] == resp_jsobj["biography"]
        assert metadata_dict["photo_res_horiz"] == resp_jsobj["photo_res_horiz"]
        assert metadata_dict["photo_res_vert"] == resp_jsobj["photo_res_vert"]
        assert metadata_dict["photo_url"] == resp_jsobj["photo_url"]

        metadata_obj = db.session.query(AuthorMetadata).get(
            resp_jsobj["author_metadata_id"]
        )
        assert metadata_dict["age"] == metadata_obj.age
        assert metadata_dict["biography"] == metadata_obj.biography
        assert metadata_dict["photo_res_horiz"] == metadata_obj.photo_res_horiz
        assert metadata_dict["photo_res_vert"] == metadata_obj.photo_res_vert
        assert metadata_dict["photo_url"] == metadata_obj.photo_url

        assert resp_jsobj["author_id"] == metadata_obj.author_id

        return resp_jsobj, metadata_obj

    @classmethod
    def test_author_resp(cls, response, author_dict):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        assert author_dict["first_name"] == resp_jsobj["first_name"]
        assert author_dict["last_name"] == resp_jsobj["last_name"]

        author_obj = db.session.query(Author).get(resp_jsobj["author_id"])
        assert author_dict["first_name"] == author_obj.first_name
        assert author_dict["last_name"] == author_obj.last_name

        assert resp_jsobj["author_id"] == author_obj.author_id

        return resp_jsobj, author_obj

    @classmethod
    def cleanup__empty_all_tables(cls):
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
