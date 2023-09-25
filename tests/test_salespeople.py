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


# Testing POST /salespeople/<id>/clients endpoint
def test_create_salesperson_client_endpoint(db_w_cleanup, staged_app_client):  # 57/83
    app, client = staged_app_client

    # Refactored test setup bc it's the same every time
    def _setup():
        salesperson_obj = Genius.gen_salesperson_obj()
        client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
        return salesperson_obj.salesperson_id, client_dict

    salesperson_id, client_dict = _setup()

    response = client.post(f"/salespeople/{salesperson_id}/clients", json=client_dict)
    resp_jsobj, client_obj = DbBasedTester.test_client_resp(response, client_dict)

    # DbBasedTester.cleanup__empty_all_tables()

    # Testing with bogus id
    bogus_salesperson_id = random.randint(1, 10)
    response = client.post(
        f"/salespeople/{bogus_salesperson_id}/clients", json=client_dict
    )
    assert response.status_code == 404

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error with unexpected or missing parameters
    salesperson_obj = Genius.gen_salesperson_obj()
    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.post(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients", json=salesperson_dict
    )
    assert response.status_code == 400, response.data


# Testing POST /salespeople endpoint
def test_create_salesperson_endpoint(db_w_cleanup, staged_app_client):  # 58/83
    app, client = staged_app_client

    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.post("/salespeople", json=salesperson_dict)

    DbBasedTester.test_salesperson_resp(response, salesperson_dict)

    DbBasedTester.cleanup__empty_all_tables()

    client_dict = Genius.gen_client_dict()
    response = client.post("/salespeople", json=client_dict)
    assert response.status_code == 400, response.data


# Testing DELETE /salespeople/<id> endpoint
def test_delete_salesperson_by_id_endpoint(db_w_cleanup, staged_app_client):  # 59/83
    db = db_w_cleanup
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    salesperson_id = salesperson_obj.salesperson_id

    client_obj = Genius.gen_client_obj()
    client_id = client_obj.client_id

    response = client.delete(f"/salespeople/{salesperson_obj.salesperson_id}")
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Salesperson).get(salesperson_id) is None
    assert db.session.query(Client).get(client_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    bogus_salesperson_id = random.randint(1, 10)
    response = client.delete(f"/salespeople/{bogus_salesperson_id}")
    assert response.status_code == 404


# Testing DELETE /salespeople/<id>/clients/<id> endpoint
def test_delete_salesperson_client_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 60/83
    db = db_w_cleanup
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    client_id = client_obj.client_id

    response = client.delete(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{client_id}"
    )
    assert response.status_code == 200
    assert json.loads(response.data) is True
    assert db.session.query(Client).get(client_id) is None

    DbBasedTester.cleanup__empty_all_tables()

    client_obj = Genius.gen_client_obj()
    bogus_salesperson_id = random.randint(1, 10)
    response = client.delete(
        f"/salespeople/{bogus_salesperson_id}/clients/{client_obj.client_id}"
    )
    assert response.status_code == 404
    assert db.session.query(Client).get(client_obj.client_id) is not None

    DbBasedTester.cleanup__empty_all_tables()

    salesperson_obj = Genius.gen_salesperson_obj()
    bogus_client_id = random.randint(1, 10)
    response = client.delete(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{bogus_client_id}"
    )
    assert response.status_code == 404


# Testing GET /salespeople/<id> endpoint
def test_display_salesperson_by_id_endpoint(db_w_cleanup, staged_app_client):  # 61/83
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()

    response = client.get(f"/salespeople/{salesperson_obj.salesperson_id}")
    DbBasedTester.test_salesperson_resp(response, salesperson_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_salesperson_id = random.randint(1, 10)
    response = client.get(f"/salespeople/{bogus_salesperson_id}")
    assert response.status_code == 404, response.data


# Testing GET /salespeople/<id>/clients/<id> endpoint
def test_display_salesperson_client_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 62/83
    app, client = staged_app_client

    # Testing base case
    salesperson_obj = Genius.gen_salesperson_obj()
    client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
    response = client.get(
        f"/salespeople/{salesperson_obj.salesperson_id}"
        + f"/clients/{client_obj.client_id}"
    )
    assert response.status_code == 200, response.data
    DbBasedTester.test_client_resp(response, client_obj)

    DbBasedTester.cleanup__empty_all_tables()

    bogus_salesperson_id = random.randint(1, 10)
    bogus_client_id = random.randint(1, 10)
    response = client.get(
        f"/salespeople/{bogus_salesperson_id}/clients/{bogus_client_id}"
    )
    assert response.status_code == 404, response.data


# Testing GET /salespeople/<id>/clients endpoint
def test_display_salesperson_clients_endpoint(db_w_cleanup, staged_app_client):  # 63/83
    app, client = staged_app_client

    salesperson_obj = Genius.gen_salesperson_obj()
    client_objs_l = [
        Genius.gen_client_obj(salesperson_obj.salesperson_id) for _ in range(3)
    ]
    response = client.get(f"/salespeople/{salesperson_obj.salesperson_id}/clients")
    assert response.status_code == 200, response.data
    client_jsobj_l = json.loads(response.data)
    client_jsobj_obj_matches = dict()
    for client_obj in client_objs_l:
        client_jsobj_obj_matches[client_obj.client_id] = operator.concat(
            [client_obj],
            list(
                filter(
                    lambda jsobj: jsobj["client_id"] == client_obj.client_id,
                    client_jsobj_l,
                )
            ),
        )

    for client_obj, client_jsobj in client_jsobj_obj_matches.values():
        assert client_jsobj["email_address"] == client_obj.email_address
        assert client_jsobj["phone_number"] == client_obj.phone_number
        assert client_jsobj["business_name"] == client_obj.business_name
        assert client_jsobj["street_address"] == client_obj.street_address
        assert client_jsobj["city"] == client_obj.city
        assert client_jsobj["state"] == client_obj.state
        assert client_jsobj["zipcode"] == client_obj.zipcode
        assert client_jsobj["country"] == client_obj.country

    DbBasedTester.cleanup__empty_all_tables()

    bogus_salesperson_id = random.randint(1, 10)
    response = client.get(f"/salespeople/{bogus_salesperson_id}/clients")
    assert response.status_code == 404, response.data


# Testing GET /salespeople
def test_index_endpoint(db_w_cleanup, staged_app_client):  # 64/83
    db = db_w_cleanup
    app, client = staged_app_client

    salesperson_dicts = [Genius.gen_salesperson_dict() for _ in range(10)]
    for salesperson_dict in salesperson_dicts:
        db.session.add(Salesperson(**salesperson_dict))
    db.session.commit()
    response = client.get("/salespeople")
    assert response.status_code == 200
    for salesperson_jsobj in response.get_json():
        assert any(
            salesperson_dict["first_name"] == salesperson_jsobj["first_name"]
            and salesperson_dict["last_name"] == salesperson_jsobj["last_name"]
            and salesperson_dict["salary"] == salesperson_jsobj["salary"]
            for salesperson_dict in salesperson_dicts
        )


# Testing PATCH /salespeople/<id> endpoint
def test_update_salesperson_by_id_endpoint(db_w_cleanup, staged_app_client):  # 65/83
    app, client = staged_app_client

    # Testing base case
    salesperson_obj = Genius.gen_salesperson_obj()
    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}", json=salesperson_dict
    )
    DbBasedTester.test_salesperson_resp(response, salesperson_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    salesperson_obj = Genius.gen_salesperson_obj()
    response = client.patch(f"/salespeople/{salesperson_obj.salesperson_id}", json={})
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if salesperson_id is bogus
    bogus_salesperson_id = random.randint(1, 10)
    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.patch(
        f"/salespeople/{bogus_salesperson_id}", json=salesperson_dict
    )
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    salesperson_obj = Genius.gen_salesperson_obj()
    client_dict = Genius.gen_client_dict()
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}", json=client_dict
    )
    assert response.status_code == 400, response.data


# Testing PATCH /salespeople/<id>/clients/<id> endpoint
def test_update_salesperson_client_by_id_endpoint(
    db_w_cleanup, staged_app_client
):  # 66/83
    app, client = staged_app_client

    def _setup():
        salesperson_obj = Genius.gen_salesperson_obj()
        client_obj = Genius.gen_client_obj(salesperson_obj.salesperson_id)
        return salesperson_obj, client_obj

    # Testing base case
    salesperson_obj, client_obj = _setup()
    client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{client_obj.client_id}",
        json=client_dict,
    )
    DbBasedTester.test_client_resp(response, client_dict)

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 400 error if PATCHed json is empty
    salesperson_obj, client_obj = _setup()
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{client_obj.client_id}",
        json={},
    )
    assert response.status_code == 400, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if salesperson_id is bogus
    salesperson_obj, client_obj = _setup()
    client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
    bogus_salesperson_id = randint_excluding(1, 10, salesperson_obj.salesperson_id)
    assert salesperson_obj is not None
    response = client.patch(
        f"/salespeople/{bogus_salesperson_id}/clients/{client_obj.client_id}",
        json=client_dict,
    )
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # Testing for 404 error if client_id is bogus
    salesperson_obj, client_obj = _setup()
    client_dict = Genius.gen_client_dict(salesperson_obj.salesperson_id)
    bogus_client_id = randint_excluding(1, 10, client_obj.client_id)
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{bogus_client_id}",
        json=client_dict,
    )
    assert response.status_code == 404, response.data

    DbBasedTester.cleanup__empty_all_tables()

    # test for unexpected params and missing params
    salesperson_obj, client_obj = _setup()
    salesperson_dict = Genius.gen_salesperson_dict()
    response = client.patch(
        f"/salespeople/{salesperson_obj.salesperson_id}/clients/{client_obj.client_id}",
        json=salesperson_dict,
    )
    assert response.status_code == 400, response.data
