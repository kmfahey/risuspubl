#!/usr/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    crt_tbl_row_clos,
    check_json_req_props,
    del_tbl_row_by_id_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_clos,
    handle_exc,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Client


blueprint = Blueprint("clients", __name__, url_prefix="/clients")


# These functions return closures that implement the requested
# functions, filling in the blank(s) with the provided class objects.
crt_clnt = crt_tbl_row_clos(Client)
del_clnt_by_id = del_tbl_row_by_id_clos(Client)
disp_clnt_by_id = disp_tbl_row_by_id_clos(Client)
disp_clnts = disp_tbl_rows_clos(Client)
upd_clnt_by_id = updt_tbl_row_by_id_clos(Client)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /clients endpoint. All rows in the clients table
    are loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_clnts()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:client_id>", methods=["GET"])
def disp_clnt_by_clid_endpt(client_id: int):
    """
    Implements a GET /clients/{client_id} endpoint. The row in the
    clients table with the given client_id is loaded and output in JSON.

    :client_id: The client_id of the row in the clients table to load
    and display.
    :return: A flask.Response object.
    """
    try:
        return disp_clnt_by_id(client_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["POST"])
def crt_clnt_endpt():
    """
    Implements a POST /clients endpoint. A new row in the clients table
    is constituted from the JSON parameters and saved to that table.

    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Client, request.json, {"client_id"})
        return crt_clnt(request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:client_id>", methods=["PATCH", "PUT"])
def updt_clnt_by_clid_endpt(client_id: int):
    """
    Implements a PATCH /clients/{client_id} endpoint. The row in
    the clients table with that client_id is updated from the JSON
    parameters.

    :client_id: The client_id of the row in the clients table to update.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Client, request.json, {"client_id"}, chk_missing=False)
        return upd_clnt_by_id(client_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:client_id>", methods=["DELETE"])
def del_clnt_by_clid_endpt(client_id: int):
    """
    Implements a DELETE /clients/{client_id} endpoint. The row in the
    clients table with that client_id is deleted.

    :client_id: The client_id of the row in the clients table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_clnt_by_id(client_id)
    except Exception as exception:
        return handle_exc(exception)
