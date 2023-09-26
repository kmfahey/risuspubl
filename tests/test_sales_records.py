#!/usr/bin/python3

import os
import random
import itertools

import pytest

from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing GET /sales_records/<id> endpoint
def test_display_sales_record_endpoint(db_w_cleanup, staged_app_client):  # 67/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    sales_record_obj = Genius.gen_sales_record_obj(book_obj.book_id)
    response = client.get(f"/sales_records/{sales_record_obj.sales_record_id}")
    DbBasedTester.test_sales_record_resp(response, sales_record_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus sales_record_id
    bogus_sales_record_id = random.randint(1, 10)
    response = client.get(f"/sales_records/{bogus_sales_record_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /sales_records/books/<id> endpoint
def test_display_sales_records_by_book_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 68/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    sales_record_objs_l = [
        Genius.gen_sales_record_obj(book_obj.book_id) for _ in range(10)
    ]
    response = client.get(f"/sales_records/books/{book_obj.book_id}")

    assert response.status_code == 200, response.data.decode("utf8")
    for sales_record_jsobj in response.get_json():
        assert any(
            sales_record_jsobj["year"] == sales_record_obj.year
            and sales_record_jsobj["month"] == sales_record_obj.month
            and sales_record_jsobj["copies_sold"] == sales_record_obj.copies_sold
            and sales_record_jsobj["gross_profit"]
            == float(sales_record_obj.gross_profit)
            and sales_record_jsobj["net_profit"] == float(sales_record_obj.net_profit)
            for sales_record_obj in sales_record_objs_l
        )

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus sales_record_id
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/sales_record/books/{bogus_book_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /sales_records/years/<year>/books/<id> endpoint
def test_display_sales_records_by_year_and_book_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 69/83
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    year = Genius.todays_date.year - 1
    if year <= book_obj.publication_date.year <= Genius.todays_date.year:
        book_obj.publication_date = book_obj.publication_date.replace(year=year - 1)
    sales_record_objs_d = {
        month: Genius.gen_sales_record_obj(book_obj.book_id, year, month)
        for month in range(1, 13)
    }
    response = client.get(f"/sales_records/years/{year}/books/{book_obj.book_id}")

    assert response.status_code == 200, response.data.decode("utf8")
    for month, sales_record_jsobj in zip(range(1, 13), response.get_json()):
        sales_record_obj = sales_record_objs_d[month]
        assert sales_record_jsobj["year"] == sales_record_obj.year == year
        assert sales_record_jsobj["month"] == sales_record_obj.month == month
        assert sales_record_jsobj["copies_sold"] == sales_record_obj.copies_sold
        assert sales_record_jsobj["gross_profit"] == float(
            sales_record_obj.gross_profit
        )
        assert sales_record_jsobj["net_profit"] == float(sales_record_obj.net_profit)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus sales_record_id
    bogus_book_id = random.randint(1, 10)
    response = client.get(f"/sales_records/years/{year}/books/{bogus_book_id}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /sales_records/years/<year>/months/<month>/books/<id> endpoint
def test_display_sales_records_by_year_and_month_and_book_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 70/83
    db = db_w_cleanup
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    year = Genius.todays_date.year - 1
    if year <= book_obj.publication_date.year <= Genius.todays_date.year:
        book_obj.publication_date = book_obj.publication_date.replace(year=year - 1)
    db.session.commit()
    sales_record_objs_d = {
        month: Genius.gen_sales_record_obj(book_obj.book_id, year, month)
        for month in range(1, 13)
    }
    month = random.randint(1, 12)
    response = client.get(
        f"/sales_records/years/{year}/months/{month}/books/{book_obj.book_id}"
    )
    DbBasedTester.test_sales_record_resp(response, sales_record_objs_d[month])

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus sales_record_id
    bogus_book_id = random.randint(1, 10)
    response = client.get(
        f"/sales_records/years/{year}/months/{month}/books/{bogus_book_id}"
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a month for which there is no
    # record
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    year = Genius.todays_date.year - 1
    if year <= book_obj.publication_date.year <= Genius.todays_date.year:
        book_obj.publication_date = book_obj.publication_date.replace(year=year - 1)
    db.session.commit()
    [Genius.gen_sales_record_obj(book_obj.book_id, year, month) for month in range(1, 12)]
    response = client.get(
        f"/sales_records/years/{year}/months/12/books/{book_obj.book_id}"
    )
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a year for which there is no
    # record
    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    year = Genius.todays_date.year - 1
    if year <= book_obj.publication_date.year <= Genius.todays_date.year:
        book_obj.publication_date = book_obj.publication_date.replace(year=year - 1)
    db.session.commit()
    [Genius.gen_sales_record_obj(book_obj.book_id, year, month) for month in range(1, 13)]
    other_year = randint_excluding(2000, 2020, year)
    response = client.get(
        f"/sales_records/years/{other_year}/months/{month}/books/{book_obj.book_id}"
    )
    assert response.status_code == 404, response.data.decode("utf8")


def _setup_for_display_by_date(db, year, *months):
    editor_obj = Genius.gen_editor_obj()
    book_objs_l = [Genius.gen_book_obj(editor_obj.editor_id) for _ in range(3)]
    for book_obj in book_objs_l:
        # If the book's randomly generated publication date is this year or
        # last year, it's too recent. Correcting it to be older than last year
        # which we're generating testing data in.
        if year <= book_obj.publication_date.year <= Genius.todays_date.year:
            book_obj.publication_date = book_obj.publication_date.replace(year=year - 1)
    db.session.commit()
    sales_record_objs_l = list(
        *itertools.chain(
            (
                Genius.gen_sales_record_obj(book_obj.book_id, year, month)
                for book_obj in book_objs_l
            )
            for month in months
        )
    )
    return editor_obj, book_objs_l, sales_record_objs_l


# Testing GET /sales_records/years/<year>/month/<month> endpoint
def test_display_sales_records_by_year_and_month_endpoint(
    db_w_cleanup, staged_app_client
):  # 71/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    year = Genius.todays_date.year - 1
    month = random.randint(1, 12)
    _, _, sales_record_objs_l = _setup_for_display_by_date(db, year, month)

    response = client.get(f"/sales_records/years/{year}/months/{month}")

    assert response.status_code == 200, response.data.decode("utf8")
    for sales_record_jsobj in response.get_json():
        assert any(
            sales_record_jsobj["year"] == sales_record_obj.year
            and sales_record_jsobj["month"] == sales_record_obj.month
            and sales_record_jsobj["copies_sold"] == sales_record_obj.copies_sold
            and sales_record_jsobj["gross_profit"]
            == float(sales_record_obj.gross_profit)
            and sales_record_jsobj["net_profit"] == float(sales_record_obj.net_profit)
            for sales_record_obj in sales_record_objs_l
        )

    DbBasedTester.cleanup__empty_all_tables()

    # Testing 404 error with empty month
    year = Genius.todays_date.year - 1
    month = random.randint(1, 12)
    _setup_for_display_by_date(db, year, month)
    different_month = randint_excluding(1, 12, month)
    response = client.get(f"/sales_records/years/{year}/months/{different_month}")
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing 404 error with empty year
    year = Genius.todays_date.year - 1
    month = random.randint(1, 12)
    _setup_for_display_by_date(db, year, month)
    different_year = randint_excluding(1990, Genius.todays_date.year, year)
    response = client.get(f"/sales_records/years/{different_year}/months/{month}")
    assert response.status_code == 404, response.data.decode("utf8")


# Testing GET /sales_records/years/<year> endpoint
def test_display_sales_records_by_year_endpoint(
    db_w_cleanup, staged_app_client
):  # 72/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    year = Genius.todays_date.year - 1
    month = random.randint(1, 12)
    _, _, sales_record_objs_l = _setup_for_display_by_date(db, year, month)

    response = client.get(f"/sales_records/years/{year}/months/{month}")

    assert response.status_code == 200, response.data.decode("utf8")
    for sales_record_jsobj in response.get_json():
        assert any(
            sales_record_jsobj["year"] == sales_record_obj.year
            and sales_record_jsobj["month"] == sales_record_obj.month
            and sales_record_jsobj["copies_sold"] == sales_record_obj.copies_sold
            and sales_record_jsobj["gross_profit"]
            == float(sales_record_obj.gross_profit)
            and sales_record_jsobj["net_profit"] == float(sales_record_obj.net_profit)
            for sales_record_obj in sales_record_objs_l
        )

    DbBasedTester.cleanup__empty_all_tables()

    # Testing 404 error with empty year
    year = Genius.todays_date.year - 1
    month = random.randint(1, 12)
    _setup_for_display_by_date(db, year, month)
    different_year = randint_excluding(1990, Genius.todays_date.year, year)
    response = client.get(f"/sales_records/years/{different_year}/months/{month}")
    assert response.status_code == 404, response.data.decode("utf8")
