#!/usr/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    check_json_req_props,
    crt_tbl_row_clos,
    del_tbl_row_by_id_clos,
    disp_tbl_row_by_id_foreign_key_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_by_foreign_id_clos,
    disp_tbl_rows_clos,
    handle_exc,
    updt_tbl_row_by_id_foreign_key_clos,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Book, Manuscript, Series


blueprint = Blueprint("series", __name__, url_prefix="/series")


# These functions return closures that implement the requested
# functions, filling in the blank(s) with the provided class objects.
crt_srs = crt_tbl_row_clos(Series)
del_srs_by_id = del_tbl_row_by_id_clos(Series)
disp_bk_by_bkid_srs_id = disp_tbl_row_by_id_foreign_key_clos(
    Series, "series_id", Book, "book_id"
)
disp_bks_by_srs_id = disp_tbl_rows_by_foreign_id_clos(Series, "series_id", Book)
disp_mscrpt_by_mscrpt_id_srs_id = disp_tbl_row_by_id_foreign_key_clos(
    Series, "series_id", Manuscript, "manuscript_id"
)
disp_mscrpts_by_srs_id = disp_tbl_rows_by_foreign_id_clos(
    Series, "series_id", Manuscript
)
disp_srs_by_id = disp_tbl_row_by_id_clos(Series)
disp_srs = disp_tbl_rows_clos(Series)
updt_bk_by_bkid_srs_id = updt_tbl_row_by_id_foreign_key_clos(
    Series, "series_id", Book, "book_id"
)
updt_mscrpt_by_mscrpt_id_srs_idr = updt_tbl_row_by_id_foreign_key_clos(
    Series, "series_id", Manuscript, "manuscript_id"
)
updt_srs_by_id = updt_tbl_row_by_id_clos(Series)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /series endpoint. All rows in the series table are
    loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_srs()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>", methods=["GET"])
def disp_srs_by_srid_endpt(series_id: int):
    """
    Implements a GET /series/{series_id} endpoint. The row in the series
    table with the given series_id is loaded and output in JSON.

    :series_id: The series_id of the row in the series table to load and
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_srs_by_id(series_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>/books", methods=["GET"])
def disp_srs_bks_endpt(series_id: int):
    """
    Implements a GET /series/{series_id}/books endpoint. All rows in
    the books table with that series_id are loaded and output as a JSON
    list.

    :series_id: The series_id associated with book_ids in the
    series_books table of rows from the books table to display.
    :return: A flask.Response object.
    """
    try:
        return disp_bks_by_srs_id(series_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>/books/<int:book_id>", methods=["GET"])
def disp_srs_bk_by_bkid_endpt(series_id: int, book_id: int):
    """
    Implements a GET /series/{series_id}/books/{book_id} endpoint. The
    row in the books table with that series_id and that book_id is
    loaded and outputed in JSON.

    :series_id: The series_id of the row in the books table to display.
    :book_id: The book_id of the row in the books table to load and
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_bk_by_bkid_srs_id(series_id, book_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>/manuscripts", methods=["GET"])
def disp_srs_mscrpts_endpt(series_id: int):
    """
    Implements a GET /series/{series_id}/manuscripts endpoint. All rows
    in the manuscripts table with that series_id are loaded and output
    as a JSON list.

    :series_id: The series_id associated with manuscript_ids in the
    series_manuscripts table of rows from the manuscripts table to
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_mscrpts_by_srs_id(series_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>/manuscripts/<int:manuscript_id>", methods=["GET"])
def disp_srs_mscrpt_by_msid_endpt(series_id: int, manuscript_id: int):
    """
    Implements a GET /series/{series_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that series_id and
    that manuscript_id is loaded and outputed in JSON.

    :series_id: The series_id of the row in the manuscripts table to
    display.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to load and display.
    :return: A flask.Response object.
    """
    try:
        return disp_mscrpt_by_mscrpt_id_srs_id(series_id, manuscript_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["POST"])
def crt_srs_endpt():
    """
    Implements a POST /series endpoint. A new row in the series table is
    constituted from the JSON parameters and saved to that table.

    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Series, request.json, {"series_id"})
        return crt_srs(request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>", methods=["PATCH", "PUT"])
def updt_srs_by_srid_endpt(series_id: int):
    """
    Implements a PATCH /series/{series_id} endpoint. The row in
    the series table with that series_id is updated from the JSON
    parameters.

    :series_id: The series_id of the row in the series table to update.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Series, request.json, {"series_id"}, chk_missing=False)
        return updt_srs_by_id(series_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>/books/<int:book_id>", methods=["PATCH", "PUT"])
def updt_srs_bk_by_bkid_endpt(series_id: int, book_id: int):
    """
    Implements a PATCH /series/{series_id}/books/{book_id} endpoint.
    The row in the books table with that book_id and that series_id is
    updated from the JSON parameters.

    :series_id: The series_id of the row in the books table to update.
    :book_id: The book_id of the row in the books table to update.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Book, request.json, {"book_id"}, chk_missing=False)
        return updt_bk_by_bkid_srs_id(series_id, book_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:series_id>/manuscripts/<int:manuscript_id>", methods=["PATCH", "PUT"]
)
def updt_srs_mscrpt_by_msid_endpt(series_id: int, manuscript_id: int):
    """
    Implements a PATCH /series/{series_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    and that series_id is updated from the JSON parameters.

    :series_id: The series_id of the row in the manuscripts table to
    update.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to update.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(
            Manuscript, request.json, {"manuscript_id"}, chk_missing=False
        )
        return updt_mscrpt_by_mscrpt_id_srs_idr(series_id, manuscript_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:series_id>", methods=["DELETE"])
def del_srs_by_srid_endpt(series_id: int):
    """
    Implements a DELETE /series/{series_id} endpoint. The row in the
    series table with that series_id is deleted.

    :series_id: The series_id of the row in the series table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_srs_by_id(series_id)
    except Exception as exception:
        return handle_exc(exception)
