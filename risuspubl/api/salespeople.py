#!/usr/bin/python3

from flask import Blueprint, jsonify, request

from risuspubl.api.utility import (
    check_json_req_props,
    crt_model_obj,
    crt_tbl_row_clos,
    del_tbl_row_by_id_foreign_key_clos,
    disp_tbl_row_by_id_foreign_key_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_by_foreign_id_clos,
    disp_tbl_rows_clos,
    gen_crt_updt_argd,
    handle_exc,
    updt_tbl_row_by_id_foreign_key_clos,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Client, Salesperson, db


blueprint = Blueprint("salespeople", __name__, url_prefix="/salespeople")


# These functions return closures that implement the requested
# functions, filling in the blank(s) with the provided class objects.


# A closure for GET /salespeople
disp_slsps = disp_tbl_rows_clos(Salesperson)

# A closure for POST /salespeople
crt_slsp = crt_tbl_row_clos(Salesperson)


# A closure for GET /salespeople/<id>
disp_slsp_by_id = disp_tbl_row_by_id_clos(Salesperson)

# A closure for PATCH /salespeople/<id>
updt_slsp_by_id = updt_tbl_row_by_id_clos(Salesperson)


# A closure for GET /salespeople/<id>/clients
disp_clnts_by_slsp_id = disp_tbl_rows_by_foreign_id_clos(
    Salesperson, "salesperson_id", Client
)


# A closure for GET /salespeople/<id>/clients/<id>
disp_clnt_by_clid_slsp_id = disp_tbl_row_by_id_foreign_key_clos(
    Salesperson, "salesperson_id", Client, "client_id"
)

# A closure for PATCH /salespeople/<id>/clients/<id>
updt_clnt_by_clid_slsp_id = updt_tbl_row_by_id_foreign_key_clos(
    Salesperson, "salesperson_id", Client, "client_id"
)

# A closure for DELETE /salespeople/<id>/clients/<id>
del_clnt_by_clid_slsp_id = del_tbl_row_by_id_foreign_key_clos(
    Salesperson, "salesperson_id", Client, "client_id"
)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /salespeople endpoint. All rows in the salespeople
    table are loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_slsps()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>", methods=["GET"])
def disp_slsp_by_slpid_endpt(salesperson_id: int):
    """
    Implements a GET /salespeople/{salesperson_id} endpoint. The row in
    the salespeople table with the given salesperson_id is loaded and
    output in JSON.


    :salesperson_id: The salesperson_id of the row in the salespeople
    table to load and display.
    :return: A flask.Response object.
    """
    try:
        return disp_slsp_by_id(salesperson_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>/clients", methods=["GET"])
def disp_slsp_clients_endpt(salesperson_id: int):
    """
    Implements a GET /salespeople/{salesperson_id}/clients endpoint. All
    rows in the clients table with that salesperson_id are loaded and
    output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients
    table to display.
    :return: A flask.Response object.
    """
    try:
        return disp_clnts_by_slsp_id(salesperson_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>/clients/<int:client_id>", methods=["GET"])
def disp_slsp_clnt_by_slpid_endpt(salesperson_id: int, client_id: int):
    """
    Implements a GET /salespeople/{salesperson_id}/clients endpoint. All
    rows in the clients table with that salesperson_id are loaded and
    output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients
    table to display.
    :return: A flask.Response object.
    """
    try:
        return disp_clnt_by_clid_slsp_id(salesperson_id, client_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["POST"])
def crt_slsp_endpt():
    """
    Implements a POST /salespeople endpoint. A new row in the
    salespeople table is constituted from the JSON parameters and saved
    to that table.

    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Salesperson, request.json, {"salesperson_id"})
        return crt_slsp(request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>/clients", methods=["POST"])
def crt_slsp_clnt_endpt(salesperson_id: int):
    """
    Implements a POST /salespeople/{salesperson_id}/clients endpoint. A
    new row in the clients table is constituted from the JSON parameters
    and that salesperson_id and saved to that table.

    :salesperson_id: The salesperson_id to save to the new row in the
    clients table.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Client, request.json, {"client_id"})
        Salesperson.query.get_or_404(salesperson_id)
        # Using crt_model_obj() to process request.json into a Client()
        # argument dict and instance a Client() object.
        client_obj = crt_model_obj(
            Client,
            gen_crt_updt_argd(Client, request.json, salesperson_id=salesperson_id),
        )
        client_obj.salesperson_id = salesperson_id
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>", methods=["PATCH", "PUT"])
def updt_slsp_by_slpid_endpt(salesperson_id: int):
    """
    Implements a PATCH /salespeople/{salesperson_id} endpoint. The row
    in the salespeople table with that salesperson_id is updated from
    the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the salespeople
    table to update.
    :return: A flask.Response object.
    """
    try:
        return updt_slsp_by_id(salesperson_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:salesperson_id>/clients/<int:client_id>", methods=["PATCH", "PUT"]
)
def updt_slsp_clnt_by_clid_endpt(salesperson_id: int, client_id: int):
    """
    Implements a PATCH /salespeople/{salesperson_id}/clients/{client_id}
    endpoint. The row in the clients table with that client_id and that
    salesperson_id is updated from the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the clients table
    to update.
    :client_id: The client_id of the row in the clients table to update.
    :return: A flask.Response object.
    """
    try:
        if not len(request.json):
            raise ValueError(
                "update action executed with no parameters indicating "
                + "fields to update"
            )
        check_json_req_props(Client, request.json, {"client_id"}, chk_missing=False)
        return updt_clnt_by_clid_slsp_id(salesperson_id, client_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>", methods=["DELETE"])
def del_slsp_by_slpid_endpt(salesperson_id: int):
    """
    Implements a DELETE /salespeople/{salesperson_id} endpoint. The row
    in the salespeople table with that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the salespeople
    table to delete.
    :return: A flask.Response object.
    """
    try:
        salesperson_obj = Salesperson.query.get_or_404(salesperson_id)
        # Finding all Client objects with the salesperson_id column set
        # to this value and resetting it to None for each one.
        client_objs = Client.query.filter(Client.salesperson_id == salesperson_id)
        for client_obj in client_objs:
            client_obj.salesperson_id = None
        db.session.commit()
        db.session.delete(salesperson_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:salesperson_id>/clients/<int:client_id>", methods=["DELETE"])
def del_slsp_clnt_by_slpid_endpt(salesperson_id: int, client_id: int):
    """
    Implements a DELETE
    /salespeople/{salesperson_id}/clients/{client_id} endpoint. The row
    in the clients table with that client_id and that salesperson_id is
    deleted.

    :salesperson_id: The salesperson_id of the row in the clients table
    to delete.
    :client_id: The client_id value of the row in the clients table to
    delete.
    :return: A flask.Response object.
    """
    try:
        return del_clnt_by_clid_slsp_id(salesperson_id, client_id)
    except Exception as exception:
        return handle_exc(exception)
