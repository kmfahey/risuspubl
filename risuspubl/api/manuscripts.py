#!/usr/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    del_tbl_row_by_id_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_clos,
    handle_exc,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Manuscript


blueprint = Blueprint("manuscripts", __name__, url_prefix="/manuscripts")


# These functions return closures that implement the requested
# functions, filling in the blank(s) with the provided class objects.


# A closure for GET /manuscripts
disp_mscrpts = disp_tbl_rows_clos(Manuscript)


# A closure for GET /manuscripts/<id>
disp_mscrpt_by_msid = disp_tbl_row_by_id_clos(Manuscript)

# A closure for PATCH /manuscripts/<id>
updt_mscrpt_by_msd = updt_tbl_row_by_id_clos(Manuscript)

# A closure for DELETE /manuscripts/<id>
del_mscrpt_by_msid = del_tbl_row_by_id_clos(Manuscript)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts
    table are loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_mscrpts()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:manuscript_id>", methods=["GET"])
def disp_mscrpt_by_msid_endpt(manuscript_id: int):
    """
    Implements a GET /manuscripts/{manuscript_id} endpoint. The row in
    the manuscripts table with the given manuscript_id is loaded and
    output in JSON.

    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to load and display.
    :return: A flask.Response object.
    """
    try:
        return disp_mscrpt_by_msid(manuscript_id)
    except Exception as exception:
        return handle_exc(exception)


# A Create endpoint is deliberately not implemented, because
# without a way to specify the author or authors to attach
# the manuscript to, no entry in the authors_manuscripts
# table would be created and the manuscript would an orphan
# in the database. /authors/<author_id>/manuscripts and
# /authors/<author1_id>/<author2_id>/manuscripts already accept Create
# actions and when done that way associations with an author or authors
# can be created appropriately.


@blueprint.route("/<int:manuscript_id>", methods=["PATCH", "PUT"])
def updt_mscrpt_by_msid_endpt(manuscript_id: int):
    """
    Implements a PATCH /manuscripts/{manuscript_id} endpoint. The row in
    the manuscripts table with that manuscript_id is updated from the
    JSON parameters.


    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to update.
    :return: A flask.Response object.
    """
    try:
        return updt_mscrpt_by_msd(manuscript_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:manuscript_id>", methods=["DELETE"])
def del_mscrpt_by_msid_endpt(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/{manuscript_id} endpoint. The row
    in the manuscripts table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_mscrpt_by_msid(manuscript_id)
    except Exception as exception:
        return handle_exc(exception)
