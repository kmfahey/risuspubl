#!/usr/bin/python3

import os
import re

from collections import defaultdict
from functools import partial as curry


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# Testing the GET /authors endpoint -- test 84 of 84
def test_docroot_endpoint(db_w_cleanup, staged_app_client):
    app, client = staged_app_client

    response = client.get("/")
    assert response.status_code == 200, response.data

    # The response data expresses its endpoints with variables expressed
    # Insomnia-style: {{authorId}}. Replacing those with generic <id>.
    response_data = response.get_json()

    # Copying to a second dict bc we're changing a dict's keys and doing
    # that during iteration gets you a RuntimeError.
    respdat_simplf = dict()
    for section, endpts_d in response_data.items():
        respdat_simplf[section] = dict()
        for endpt, methods_d in endpts_d.items():
            endpt_w_id, _ = re.subn("{{[^{}]+}}", "<id>", endpt)
            respdat_simplf[section][endpt_w_id] = methods_d

    # The rules gotten from flask express the endpoints with variables
    # in flask style: <int:author_id>. Replacing those with generic
    # <id>.
    accept_mth = ["GET", "POST", "PATCH", "DELETE"]

    flask_rules = defaultdict(curry(defaultdict, list))
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            path, _ = re.subn(r"<[^<>]+>", "<id>", rule.rule)
            (method,) = filter(accept_mth.__contains__, rule.methods)
            section = path.split("/", 2)[1]
            if section == "static":
                continue
            elif not section:
                section = "docroot"
            flask_rules[section][path].append(method)

    # flask_rules and respdat_simplf now express endpoint paths in the
    # same format so assertions of equality will work.
    for section, endpts_d in flask_rules.items():
        for endpt, methods in endpts_d.items():
            for method in methods:
                assert method in respdat_simplf[section][endpt], (
                    f"section: {section}, endpoint: {endpt}, method: {method} "
                    + "not present in help"
                )
                del respdat_simplf[section][endpt][method]
            assert (
                len(respdat_simplf[section][endpt]) == 0
            ), f"section: {section}, endpoint: {endpt} has extra methods"
