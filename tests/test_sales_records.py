#!/usr/bin/python3

import os
import random
import pprint
import json
import operator

import pytest

from risuspubl.dbmodels import (
    Client,
    Salesperson,
)
from conftest import Genius, DbBasedTester, randint_excluding


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing GET /sales_records/<id> endpoint
def test_display_sales_record_endpoint(db_w_cleanup, staged_app_client):  # 67/83
    db = db_w_cleanup
    app, client = staged_app_client

    editor_obj = Genius.gen_editor_obj()
    book_obj = Genius.gen_book_obj(editor_obj.editor_id)
    sales_record_obj = Genius.gen_sales_record_obj(book_obj.book_id)
    response = client.get(f"/sales_records/{sales_record_obj.sales_record_id}")
    DbBasedTester.test_sales_record_resp(response, sales_record_obj)


#    DbBasedTester.cleanup__empty_all_tables()
#
#    # Testing for 404 error when called with a bogus book_id
#    bogus_book_id = random.randint(1, 10)
#    response = client.get(f"/books/{bogus_book_id}")
#    assert response.status_code == 404, response.data


## Testing GET /sales_records/books/<id> endpoint
# def test_display_sales_records_by_book_id_endpoint(db_w_cleanup, staged_app_client): # 68/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
## Testing GET /sales_records/years/<year>/books/<month> endpoint
# def test_display_sales_records_by_year_and_book_id_endpoint(db_w_cleanup, staged_app_client): # 69/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
## Testing GET /sales_records/years/<year>/months/<month>/books/<id> endpoint
# def test_display_sales_records_by_year_and_month_and_book_id_endpoint(db_w_cleanup, staged_app_client): # 70/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
## Testing GET /sales_records/years/<year>/month/<month> endpoint
# def test_display_sales_records_by_year_and_month_endpoint(db_w_cleanup, staged_app_client): # 71/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
## Testing GET /sales_records/years/<year> endpoint
# def test_display_sales_records_by_year_endpoint(db_w_cleanup, staged_app_client): # 72/83
#    db = db_w_cleanup
#    app, client = staged_app_client
#
