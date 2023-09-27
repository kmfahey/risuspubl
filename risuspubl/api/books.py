#!/usr/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    check_json_req_props,
    del_tbl_row_by_id_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_clos,
    handle_exc,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Book


blueprint = Blueprint("books", __name__, url_prefix="/books")


# These functions return closures that implement the requested
# functions, filling in the blank(s) with the provided class objects.
del_bk_by_bkid = del_tbl_row_by_id_clos(Book)
disp_bk_by_bkid = disp_tbl_row_by_id_clos(Book)
disp_bks = disp_tbl_rows_clos(Book)
updt_bk_by_bkid = updt_tbl_row_by_id_clos(Book)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /books endpoint. All rows in the books table are
    loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_bks()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:book_id>", methods=["GET"])
def disp_bk_by_bkid_endpt(book_id: int):
    """
    Implements a GET /books/{book_id} endpoint. The row in the books
    table with the given book_id is loaded and output in JSON.

    :book_id: The book_id of the row in the books table to load and
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_bk_by_bkid(book_id)
    except Exception as exception:
        return handle_exc(exception)


# A Create endpoint is deliberately not implemented, because without
# a way to specify the author or authors to attach the book to, no
# entry in the authors_books table would be created and the book
# would an orphan in the database. /authors/<author_id>/books and
# /authors/<author1_id>/<author2_id>/books already accept Create actions
# and when done that way associations with an author or authors can be
# created appropriately.


@blueprint.route("/<int:book_id>", methods=["PATCH", "PUT"])
def updt_bk_by_bkid_endpt(book_id: int):
    """
    Implements a PATCH /books/{book_id} endpoint. The row in the books
    table with that book_id is updated from the JSON parameters.

    :book_id: The book_id of the row in the books table to update.
    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Book, request.json, {"book_id"}, chk_missing=False)
        return updt_bk_by_bkid(book_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:book_id>", methods=["DELETE"])
def del_bk_by_bkid_endpt(book_id: int):
    """
    Implements a DELETE /books/{book_id} endpoint. The row in the books
    table with that book_id is deleted.

    :book_id: The book_id of the row in the books table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_bk_by_bkid(book_id)
    except Exception as exception:
        return handle_exc(exception)
