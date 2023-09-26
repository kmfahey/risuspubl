#!/usr/bin/python3

import math
import os
import random
import itertools
from datetime import date, timedelta

import faker
import pytest
import psycopg2

from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    AuthorsBooks,
    AuthorsManuscripts,
    Book,
    Client,
    Editor,
    Manuscript,
    SalesRecord,
    Salesperson,
    Series,
    db,
)
from risuspubl.flaskapp import create_app


# Set environment variable for Flask's configuration
os.environ[
    "FLASK_ENV"
] = "testing"  # This should be set before creating the app instance.


def randint_excluding(lb, ub, *exclints):
    intval = random.randint(lb, ub)
    while any(intval == exclint for exclint in exclints):
        intval = random.randint(lb, ub)
    return intval


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

    # If the above connection succeeded, the user exists. Now, check for the
    # database's existence.
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


# called it Genius because Generator already has a definition in python.
class Genius:
    faker_obj = faker.Faker()

    todays_date = date.today()

    lorem_ipsum = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor \
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis \
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. \
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore \
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt \
in culpa qui officia deserunt mollit anim id est laborum."""

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

    business_names = [
        "Spinka & Sons Co.",
        "Rippin LLC",
        "Dickinson, Hodkiewicz & Trantow Co.",
        "Bartoletti, Stoltenberg & Herzog Co.",
        "Greenholt, Hane & Emard Co.",
        "Ziemann & McClure Co.",
        "Heaney Inc",
        "Durgan Group",
        "O'Connell & Fisher Co.",
        "Keeling & Sons Co.",
    ]

    street_addresses = [
        "62 Delaware St.",
        "239 Paris Hill St.",
        "344 Studebaker Ave.",
        "205 Sunnyslope Street",
        "964 San Juan Dr.",
        "806 Ivy Ave.",
        "76 Lookout Lane",
        "17 Cemetery Road",
        "8987 S. North Court",
        "114C Southampton Ave.",
    ]

    hexdigit_cp = tuple(range(48, 58)) + tuple(range(97, 103))

    @classmethod
    def gen_hexdigits(cls, number_of_chars):
        return "".join(
            chr(random.choice(cls.hexdigit_cp)) for _ in range(number_of_chars)
        )

    @classmethod
    def gen_author_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(), last_name=cls.faker_obj.last_name()
        )

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
    def gen_client_dict(cls, salesperson_id=None):
        retdict = dict(
            email_address=cls.faker_obj.email(),
            phone_number=str(random.randint(10000000000, 19999999999)),
            business_name=random.choice(cls.business_names),
            street_address=random.choice(cls.street_addresses),
            city=cls.faker_obj.city(),
            state=cls.faker_obj.state_abbr(),
            zipcode=str(random.randint(100000000, 999999999)),
            country="USA",
        )
        if salesperson_id is not None:
            retdict["salesperson_id"] = salesperson_id
        return retdict

    @classmethod
    def gen_editor_dict(cls):
        return dict(
            first_name=cls.faker_obj.first_name(),
            last_name=cls.faker_obj.last_name(),
            salary=random.randint(65, 95) * 1000,
        )

    @classmethod
    def gen_manuscript_dict(cls, editor_id=None, series_id=None):
        retdict = dict(
            advance=random.randint(10, 20) * 1000,
            due_date=cls.faker_obj.date_between_dates(
                cls.todays_date + timedelta(days=1),
                date(cls.todays_date.year + 2, cls.todays_date.month, 1),
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
    def gen_metadata_dict(cls, author_id=None):
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
    def gen_sales_record_dict(cls, book_id):
        book_obj = db.session.query(Book).get(book_id)

        publ_year = book_obj.publication_date.year
        this_year = cls.todays_date.year
        rand_year = random.randint(publ_year, this_year)
        match rand_year:
            case int(publ_year):
                rand_month = random.randint(book_obj.publication_date.month, 12)
            case int(this_year):
                rand_month = random.randint(1, cls.todays_date.month)
            case _:
                rand_month = random.randint(1, 12)

        profit_margin = random.uniform(0.075, 0.125)
        copies_sold = round(random.gauss(87.5, 20))
        # Generates random profit amounts from random.gauss(12.5, 5) dropping
        # results <= 0 and sums them
        gross_profit = round(
            sum(
                itertools.islice(
                    filter(
                        lambda copies_sold: copies_sold > 0,
                        (round(random.gauss(12.5, 5), 2) for _ in itertools.count()),
                    ),
                    copies_sold,
                )
            ),
            2,
        )
        net_profit = round(gross_profit * profit_margin, 2)

        return dict(
            book_id=book_id,
            year=rand_year,
            month=rand_month,
            copies_sold=copies_sold,
            gross_profit=gross_profit,
            net_profit=net_profit,
        )

    @classmethod
    def gen_salesperson_dict(cls):
        retdict = cls.gen_author_dict()
        retdict["salary"] = random.randint(60, 85) * 1000
        return retdict

    @classmethod
    def gen_series_dict(cls):
        return dict(
            title=random.choice(cls.series_titles), volumes=random.randint(1, 5)
        )

    @classmethod
    def gen_author_obj(cls):
        author_obj = Author(**cls.gen_author_dict())
        db.session.add(author_obj)
        db.session.commit()
        return author_obj

    @classmethod
    def gen_authors_books_obj(cls, author_id, book_id):
        ab_insert = AuthorsBooks.insert().values(author_id=author_id, book_id=book_id)
        db.session.execute(ab_insert)
        db.session.commit()
        return (
            db.session.query(AuthorsBooks)
            .filter_by(author_id=author_id, book_id=book_id)
            .first()
        )

    @classmethod
    def gen_authors_manuscripts_obj(cls, author_id, manuscript_id):
        ab_insert = AuthorsManuscripts.insert().values(
            author_id=author_id, manuscript_id=manuscript_id
        )
        db.session.execute(ab_insert)
        db.session.commit()
        return (
            db.session.query(AuthorsManuscripts)
            .filter_by(author_id=author_id, manuscript_id=manuscript_id)
            .first()
        )

    @classmethod
    def gen_book_obj(cls, editor_id=None, series_id=None):
        book_obj = Book(**cls.gen_book_dict(editor_id, series_id))
        db.session.add(book_obj)
        db.session.commit()
        return book_obj

    @classmethod
    def gen_client_obj(cls, salesperson_id=None):
        client_obj = Client(**cls.gen_client_dict(salesperson_id))
        db.session.add(client_obj)
        db.session.commit()
        return client_obj

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
    def gen_metadata_obj(cls, author_id):
        author_metadata_obj = AuthorMetadata(**cls.gen_metadata_dict(author_id))
        db.session.add(author_metadata_obj)
        db.session.commit()
        return author_metadata_obj

    @classmethod
    def gen_sales_record_obj(cls, book_id):
        sales_record_obj = SalesRecord(**cls.gen_sales_record_dict(book_id))
        db.session.add(sales_record_obj)
        db.session.commit()
        return sales_record_obj

    @classmethod
    def gen_salesperson_obj(cls):
        salesperson_obj = Salesperson(**cls.gen_salesperson_dict())
        db.session.add(salesperson_obj)
        db.session.commit()
        return salesperson_obj

    @classmethod
    def gen_series_obj(cls):
        series_obj = Series(**cls.gen_series_dict())
        db.session.add(series_obj)
        db.session.commit()
        return series_obj


class DbBasedTester:
    @classmethod
    def test_author_resp(cls, response, author_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(author_data, dict):
            author_dict = author_data

            assert author_dict["first_name"] == resp_jsobj["first_name"]
            assert author_dict["last_name"] == resp_jsobj["last_name"]

            author_obj = db.session.query(Author).get(resp_jsobj["author_id"])
            assert author_dict["first_name"] == author_obj.first_name
            assert author_dict["last_name"] == author_obj.last_name

        elif isinstance(author_data, Author):
            author_obj = author_data

            assert resp_jsobj["first_name"] == author_obj.first_name
            assert resp_jsobj["last_name"] == author_obj.last_name

        assert resp_jsobj["author_id"] == author_obj.author_id

        return resp_jsobj, author_obj

    @classmethod
    def test_book_resp(cls, response, book_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(book_data, dict):
            book_dict = book_data

            assert book_dict["edition_number"] == resp_jsobj["edition_number"]
            assert book_dict["editor_id"] == resp_jsobj["editor_id"]
            assert book_dict["is_in_print"] == resp_jsobj["is_in_print"]
            assert book_dict["publication_date"] == resp_jsobj["publication_date"]
            assert book_dict["title"] == resp_jsobj["title"]

            book_obj = db.session.query(Book).get(resp_jsobj["book_id"])
            assert book_dict["edition_number"] == book_obj.edition_number
            assert book_dict["editor_id"] == book_obj.editor_id
            assert book_dict["is_in_print"] == book_obj.is_in_print
            assert (
                book_dict["publication_date"] == book_obj.publication_date.isoformat()
            )
            assert book_dict["title"] == book_obj.title

        elif isinstance(book_data, Book):
            book_obj = book_data

            assert resp_jsobj["edition_number"] == book_obj.edition_number
            assert resp_jsobj["editor_id"] == book_obj.editor_id
            assert resp_jsobj["is_in_print"] == book_obj.is_in_print
            assert (
                resp_jsobj["publication_date"] == book_obj.publication_date.isoformat()
            )
            assert resp_jsobj["title"] == book_obj.title

        else:
            raise TypeError(
                "second argument had unexpected type " + type(book_data).__name__
            )

        assert resp_jsobj["book_id"] == book_obj.book_id

        return resp_jsobj, book_obj

    @classmethod
    def test_client_resp(cls, response, client_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(client_data, dict):
            client_dict = client_data

            client_dict["email_address"] == resp_jsobj["email_address"]
            client_dict["phone_number"] == resp_jsobj["phone_number"]
            client_dict["business_name"] == resp_jsobj["business_name"]
            client_dict["street_address"] == resp_jsobj["street_address"]
            client_dict["city"] == resp_jsobj["city"]
            client_dict["state"] == resp_jsobj["state"]
            client_dict["zipcode"] == resp_jsobj["zipcode"]
            client_dict["country"] == resp_jsobj["country"]

            client_obj = db.session.query(Client).get(resp_jsobj["client_id"])

            client_dict["email_address"] == client_obj.email_address
            client_dict["phone_number"] == client_obj.phone_number
            client_dict["business_name"] == client_obj.business_name
            client_dict["street_address"] == client_obj.street_address
            client_dict["city"] == client_obj.city
            client_dict["state"] == client_obj.state
            client_dict["zipcode"] == client_obj.zipcode
            client_dict["country"] == client_obj.country

        elif isinstance(client_data, Client):
            client_obj = client_data

            resp_jsobj["email_address"] == client_obj.email_address
            resp_jsobj["phone_number"] == client_obj.phone_number
            resp_jsobj["business_name"] == client_obj.business_name
            resp_jsobj["street_address"] == client_obj.street_address
            resp_jsobj["city"] == client_obj.city
            resp_jsobj["state"] == client_obj.state
            resp_jsobj["zipcode"] == client_obj.zipcode
            resp_jsobj["country"] == client_obj.country

        else:
            raise TypeError(
                "second argument had unexpected type " + type(client_data).__name__
            )

        assert resp_jsobj["client_id"] == client_obj.client_id

        return resp_jsobj, client_obj

    @classmethod
    def test_editor_resp(cls, response, editor_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(editor_data, dict):
            editor_dict = editor_data

            assert editor_dict["first_name"] == resp_jsobj["first_name"]
            assert editor_dict["last_name"] == resp_jsobj["last_name"]
            assert editor_dict["salary"] == resp_jsobj["salary"]

            editor_obj = db.session.query(Editor).get(resp_jsobj["editor_id"])
            assert editor_dict["first_name"] == editor_obj.first_name
            assert editor_dict["last_name"] == editor_obj.last_name
            assert editor_dict["salary"] == editor_obj.salary

        elif isinstance(editor_data, Editor):
            editor_obj = editor_data

            assert resp_jsobj["first_name"] == editor_obj.first_name
            assert resp_jsobj["last_name"] == editor_obj.last_name
            assert resp_jsobj["salary"] == editor_obj.salary

        assert resp_jsobj["editor_id"] == editor_obj.editor_id

        return resp_jsobj, editor_obj

    @classmethod
    def test_manuscript_resp(cls, response, manuscript_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(manuscript_data, dict):
            manuscript_dict = manuscript_data

            assert manuscript_dict["editor_id"] == resp_jsobj["editor_id"]
            assert manuscript_dict["working_title"] == resp_jsobj["working_title"]
            assert manuscript_dict["due_date"] == resp_jsobj["due_date"]
            assert manuscript_dict["advance"] == resp_jsobj["advance"]

            manuscript_obj = db.session.query(Manuscript).get(
                resp_jsobj["manuscript_id"]
            )
            assert manuscript_dict["editor_id"] == manuscript_obj.editor_id
            assert manuscript_dict["working_title"] == manuscript_obj.working_title
            assert manuscript_dict["due_date"] == manuscript_obj.due_date.isoformat()
            assert manuscript_dict["advance"] == manuscript_obj.advance

        elif isinstance(manuscript_data, Manuscript):
            manuscript_obj = manuscript_data

            assert resp_jsobj["editor_id"] == manuscript_obj.editor_id
            assert resp_jsobj["working_title"] == manuscript_obj.working_title
            assert resp_jsobj["due_date"] == manuscript_obj.due_date.isoformat()
            assert resp_jsobj["advance"] == manuscript_obj.advance

        else:
            raise TypeError(
                "second argument had unexpected type " + type(manuscript_data).__name__
            )

        assert resp_jsobj["manuscript_id"] == manuscript_obj.manuscript_id

        return resp_jsobj, manuscript_obj

    @classmethod
    def test_metadata_resp(cls, response, metadata_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(metadata_data, dict):
            metadata_dict = metadata_data

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

        elif isinstance(metadata_data, AuthorMetadata):
            metadata_obj = metadata_data

            assert resp_jsobj["age"] == metadata_obj.age
            assert resp_jsobj["biography"] == metadata_obj.biography
            assert resp_jsobj["photo_res_horiz"] == metadata_obj.photo_res_horiz
            assert resp_jsobj["photo_res_vert"] == metadata_obj.photo_res_vert
            assert resp_jsobj["photo_url"] == metadata_obj.photo_url

        else:
            raise TypeError(
                "second argument had unexpected type " + type(metadata_data).__name__
            )

        assert resp_jsobj["author_id"] == metadata_obj.author_id
        assert resp_jsobj["author_metadata_id"] == metadata_obj.author_metadata_id

        return resp_jsobj, metadata_obj

    @classmethod
    def test_sales_record_resp(cls, response, sales_record_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(sales_record_data, dict):
            sales_record_dict = sales_record_data

            assert sales_record_dict["book_id"] == resp_jsobj["book_id"]
            assert sales_record_dict["year"] == resp_jsobj["year"]
            assert sales_record_dict["month"] == resp_jsobj["month"]
            assert sales_record_dict["copies_sold"] == resp_jsobj["copies_sold"]
            assert sales_record_dict["gross_profit"] == resp_jsobj["gross_profit"]
            assert sales_record_dict["net_profit"] == resp_jsobj["net_profit"]

            sales_record_obj = db.session.query(SalesRecord).get(
                resp_jsobj["sales_record_id"]
            )

            assert sales_record_dict["book_id"] == sales_record_obj.book_id
            assert sales_record_dict["year"] == sales_record_obj.year
            assert sales_record_dict["month"] == sales_record_obj.month
            assert sales_record_dict["copies_sold"] == sales_record_obj.copies_sold
            assert sales_record_dict["gross_profit"] == float(
                sales_record_obj.gross_profit
            )
            assert sales_record_dict["net_profit"] == float(sales_record_obj.net_profit)

        elif isinstance(sales_record_data, SalesRecord):
            sales_record_obj = sales_record_data

            assert resp_jsobj["book_id"] == sales_record_obj.book_id
            assert resp_jsobj["year"] == sales_record_obj.year
            assert resp_jsobj["month"] == sales_record_obj.month
            assert resp_jsobj["copies_sold"] == sales_record_obj.copies_sold
            assert resp_jsobj["gross_profit"] == float(sales_record_obj.gross_profit)
            assert resp_jsobj["net_profit"] == float(sales_record_obj.net_profit)

        else:
            raise TypeError(
                "second argument had unexpected type "
                + type(sales_record_data).__name__
            )

        assert resp_jsobj["sales_record_id"] == sales_record_obj.sales_record_id

        return resp_jsobj, sales_record_obj

    @classmethod
    def test_salesperson_resp(cls, response, salesperson_data):
        assert response.status_code == 200, response.data

        resp_jsobj = response.get_json()
        if isinstance(salesperson_data, dict):
            salesperson_dict = salesperson_data

            assert salesperson_dict["first_name"] == resp_jsobj["first_name"]
            assert salesperson_dict["last_name"] == resp_jsobj["last_name"]
            assert salesperson_dict["salary"] == resp_jsobj["salary"]

            salesperson_obj = db.session.query(Salesperson).get(
                resp_jsobj["salesperson_id"]
            )

            assert salesperson_dict["first_name"] == salesperson_obj.first_name
            assert salesperson_dict["last_name"] == salesperson_obj.last_name
            assert salesperson_dict["salary"] == salesperson_obj.salary

        elif isinstance(salesperson_data, Salesperson):
            salesperson_obj = salesperson_data

            assert resp_jsobj["first_name"] == salesperson_obj.first_name
            assert resp_jsobj["last_name"] == salesperson_obj.last_name
            assert resp_jsobj["salary"] == salesperson_obj.salary

        else:
            raise TypeError(
                "second argument had unexpected type " + type(salesperson_data).__name__
            )

        assert resp_jsobj["salesperson_id"] == salesperson_obj.salesperson_id

        return resp_jsobj, salesperson_obj

    @classmethod
    def cleanup__empty_all_tables(cls):
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
