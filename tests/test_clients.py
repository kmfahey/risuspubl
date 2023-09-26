#!/usr/bin/python3

import os
import random

import pytest

from risuspubl.dbmodels import (
    Client,
    Salesperson,
)
from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing POST /clients
def test_client_create_endpoint(db_w_cleanup, staged_app_client):  # 35/83
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
    response = client.post("/clients", json=client_dict)
    DbBasedTester.test_client_resp(response, client_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error when sending missing or unexpected params
    book_dict = Genius.gen_book_dict()
    response = client.post("/clients", json=book_dict)
    assert response.status_code == 400, response.data.decode("utf8")


# Testing DELETE /clients/<id>
def test_delete_client_by_id_endpoint(db_w_cleanup, staged_app_client):  # 36/83
    db = db_w_cleanup
    app, client = staged_app_client

    # Testing base case
    salesperson_obj = Genius.gen_salesperson_obj()
    salesperson_id = salesperson_obj.salesperson_id
    client_obj = Genius.gen_client_obj(salesperson_id)
    client_id = client_obj.client_id
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200, response.data.decode("utf8")
    assert response.get_json() is True
    assert db.session.query(Salesperson).get(salesperson_id) is not None
    assert db.session.query(Client).get(client_id) is None

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus client_id
    bogus_client_id = random.randint(1, 10)
    response = client.delete(f"/clients/{bogus_client_id}")
    assert response.status_code == 404, response.data.decode("utf8")


#  Testing the GET /clients/<id> endpoint
def test_display_client_by_id_endpoint(db_w_cleanup, staged_app_client):  # 37/83
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    response = client.get(f"/clients/{client_obj.client_id}")
    DbBasedTester.test_client_resp(response, client_obj)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error when called with a bogus client_id
    bogus_client_id = random.randint(1, 10)
    response = client.get(f"/clients/{bogus_client_id}")
    assert response.status_code == 404, response.data.decode("utf8")


#  Testing the GET /clients endpoint
def test_index_endpoint(db_w_cleanup, staged_app_client):  # 38/83
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    client_objs_l = [
        Genius.gen_client_obj(salesperson_obj.salesperson_id) for _ in range(3)
    ]
    response = client.get("/clients")
    assert response.status_code == 200, response.data.decode("utf8")
    for client_jsobj in response.get_json():
        assert any(
            client_jsobj["email_address"] == client_obj.email_address
            and client_jsobj["phone_number"] == client_obj.phone_number
            and client_jsobj["business_name"] == client_obj.business_name
            and client_jsobj["street_address"] == client_obj.street_address
            and client_jsobj["city"] == client_obj.city
            and client_jsobj["state"] == client_obj.state
            and client_jsobj["zipcode"] == client_obj.zipcode
            and client_jsobj["country"] == client_obj.country
            for client_obj in client_objs_l
        )


# Testing the PATCH /books/<id> endpoint
def test_update_client_by_id_endpoint(db_w_cleanup, staged_app_client):  # 39/83
    app, client = staged_app_client

    # Testing base case
    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
    response = client.patch(f"/clients/{client_obj.client_id}", json=client_dict)
    DbBasedTester.test_client_resp(response, client_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    response = client.patch(f"/clients/{client_obj.client_id}", json={})
    assert response.status_code == 400, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if client_id is bogus
    bogus_client_id = random.randint(1, 10)
    client_dict = Genius.gen_client_dict()
    response = client.patch(f"/clients/{bogus_client_id}", json=client_dict)
    assert response.status_code == 404, response.data.decode("utf8")

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.patch(f"/clients/{client_obj.client_id}", json=salesperson_dict)
    assert response.status_code == 400, response.data.decode("utf8")
