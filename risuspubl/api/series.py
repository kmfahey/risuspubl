#!/usr/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    check_json_req_props,
    create_table_row_function,
    delete_table_row_by_id_function,
    display_table_row_by_id_and_foreign_key_function,
    display_table_row_by_id_function,
    display_table_rows_by_foreign_id_function,
    display_table_rows_function,
    handle_exception,
    update_table_row_by_id_and_foreign_key_function,
    update_table_row_by_id_function,
)
from risuspubl.dbmodels import Book, Manuscript, Series


blueprint = Blueprint("series", __name__, url_prefix="/series")


# These functions return closures that implement the requested functions,
# filling in the blank(s) with the provided class objects.
create_series = create_table_row_function(Series)
delete_series_by_id = delete_table_row_by_id_function(Series)
display_book_by_book_id_and_series_id = (
    display_table_row_by_id_and_foreign_key_function(
        Series, "series_id", Book, "book_id"
    )
)
display_books_by_series_id = display_table_rows_by_foreign_id_function(
    Series, "series_id", Book
)
display_manuscript_by_manuscript_id_and_series_id = (
    display_table_row_by_id_and_foreign_key_function(
        Series, "series_id", Manuscript, "manuscript_id"
    )
)
display_manuscripts_by_series_id = display_table_rows_by_foreign_id_function(
    Series, "series_id", Manuscript
)
display_series_by_id = display_table_row_by_id_function(Series)
display_series = display_table_rows_function(Series)
update_book_by_book_id_and_series_id = update_table_row_by_id_and_foreign_key_function(
    Series, "series_id", Book, "book_id"
)
update_manuscript_by_manuscript_id_and_series_idr = (
    update_table_row_by_id_and_foreign_key_function(
        Series, "series_id", Manuscript, "manuscript_id"
    )
)
update_series_by_id = update_table_row_by_id_function(Series)


@blueprint.route("", methods=["GET"])
def index_endpoint():
    """
    Implements a GET /series endpoint. All rows in the series table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return display_series()
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>", methods=["GET"])
def display_series_by_id_endpoint(series_id: int):
    """
    Implements a GET /series/{series_id} endpoint. The row in the series table
    with the given series_id is loaded and output in JSON.

    :series_id: The series_id of the row in the series table to load and
                display.
    :return:    A flask.Response object.
    """
    try:
        return display_series_by_id(series_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>/books", methods=["GET"])
def display_series_books_endpoint(series_id: int):
    """
    Implements a GET /series/{series_id}/books endpoint. All rows in the books
    table with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with book_ids in the
                series_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    try:
        return display_books_by_series_id(series_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>/books/<int:book_id>", methods=["GET"])
def display_series_book_by_id_endpoint(series_id: int, book_id: int):
    """
    Implements a GET /series/{series_id}/books/{book_id} endpoint. The row in
    the books table with that series_id and that book_id is loaded and outputed
    in JSON.

    :series_id: The series_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    try:
        return display_book_by_book_id_and_series_id(series_id, book_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>/manuscripts", methods=["GET"])
def display_series_manuscripts_endpoint(series_id: int):
    """
    Implements a GET /series/{series_id}/manuscripts endpoint. All rows in the
    manuscripts table with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with manuscript_ids in the
                series_manuscripts table of rows from the manuscripts table to
                display.
    :return:    A flask.Response object.
    """
    try:
        return display_manuscripts_by_series_id(series_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>/manuscripts/<int:manuscript_id>", methods=["GET"])
def display_series_manuscript_by_id_endpoint(series_id: int, manuscript_id: int):
    """
    Implements a GET /series/{series_id}/manuscripts/{manuscript_id} endpoint.
    The row in the manuscripts table with that series_id and that manuscript_id
    is loaded and outputed in JSON.

    :series_id:     The series_id of the row in the manuscripts table to
                    display.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    try:
        return display_manuscript_by_manuscript_id_and_series_id(
            series_id, manuscript_id
        )
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("", methods=["POST"])
def create_series_endpoint():
    """
    Implements a POST /series endpoint. A new row in the series table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        check_json_req_props(Series, request.json, {"series_id"})
        return create_series(request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>", methods=["PATCH", "PUT"])
def update_series_by_id_endpoint(series_id: int):
    """
    Implements a PATCH /series/{series_id} endpoint. The row in the series table
    with that series_id is updated from the JSON parameters.

    :series_id: The series_id of the row in the series table to update.
    :return:    A flask.Response object.
    """
    try:
        check_json_req_props(Series, request.json, {"series_id"}, chk_missing=False)
        return update_series_by_id(series_id, request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>/books/<int:book_id>", methods=["PATCH", "PUT"])
def update_series_book_by_id_endpoint(series_id: int, book_id: int):
    """
    Implements a PATCH /series/{series_id}/books/{book_id} endpoint. The row in
    the books table with that book_id and that series_id is updated from the
    JSON parameters.

    :series_id: The series_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        check_json_req_props(Book, request.json, {"book_id"}, chk_missing=False)
        return update_book_by_book_id_and_series_id(series_id, book_id, request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route(
    "/<int:series_id>/manuscripts/<int:manuscript_id>", methods=["PATCH", "PUT"]
)
def update_series_manuscript_by_id_endpoint(series_id: int, manuscript_id: int):
    """
    Implements a PATCH /series/{series_id}/manuscripts/{manuscript_id} endpoint.
    The row in the manuscripts table with that manuscript_id and that series_id
    is updated from the JSON parameters.

    :series_id: The series_id of the row in the manuscripts table to update.
    :manuscript_id:   The manuscript_id of the row in the manuscripts table to update.
    :return:    A flask.Response object.
    """
    try:
        check_json_req_props(
            Manuscript, request.json, {"manuscript_id"}, chk_missing=False
        )
        return update_manuscript_by_manuscript_id_and_series_idr(
            series_id, manuscript_id, request.json
        )
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:series_id>", methods=["DELETE"])
def delete_series_by_id_endpoint(series_id: int):
    """
    Implements a DELETE /series/{series_id} endpoint. The row in the series
    table with that series_id is deleted.

    :series_id: The series_id of the row in the series table to delete.
    :return:    A flask.Response object.
    """
    try:
        return delete_series_by_id(series_id)
    except Exception as exception:
        return handle_exception(exception)
