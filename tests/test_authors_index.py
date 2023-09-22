#!/usr/bin/python3

import os
import pprint
import json

import pytest
from risuspubl.dbmodels import Author

from conftest import Genius


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


def test_index_endpoint(db_w_cleanup, staged_app_client):  # 24/83
    db = db_w_cleanup
    app, client = staged_app_client

    author_dicts = [Genius.gen_author_dict() for _ in range(10)]
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
