#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import (
    check_json_req_props,
    create_table_row_function,
    delete_table_row_by_id_and_foreign_key_function,
    delete_table_row_by_id_function,
    display_table_row_by_id_and_foreign_key_function,
    display_table_row_by_id_function,
    display_table_rows_by_foreign_id_function,
    display_table_rows_function,
    handle_exception,
    update_table_row_by_id_and_foreign_key_function,
    update_table_row_by_id_function,
)
from risuspubl.dbmodels import Book, Editor, Manuscript


blueprint = Blueprint("editors", __name__, url_prefix="/editors")


# These functions return closures that implement the requested functions,
# filling in the blank(s) with the provided class objects.
create_editor = create_table_row_function(Editor)
delete_book_by_book_id_and_editor_id = delete_table_row_by_id_and_foreign_key_function(
    Editor, Book
)
delete_editor_by_id = delete_table_row_by_id_function(Editor)
delete_manuscript_by_manuscript_id_and_editor_id = (
    delete_table_row_by_id_and_foreign_key_function(Editor, Manuscript)
)
display_book_by_book_id_and_editor_id = (
    display_table_row_by_id_and_foreign_key_function(Editor, Book)
)
display_books_by_editor_id = display_table_rows_by_foreign_id_function(Editor, Book)
display_editor_by_id = display_table_row_by_id_function(Editor)
display_editors = display_table_rows_function(Editor)
display_manuscript_by_manuscript_id_and_editor_id = (
    display_table_row_by_id_and_foreign_key_function(Editor, Manuscript)
)
display_manuscripts_by_editor_id = display_table_rows_by_foreign_id_function(
    Editor, Manuscript
)
update_book_by_book_id_and_editor_id = update_table_row_by_id_and_foreign_key_function(
    Editor, Book
)
update_editor_by_id = update_table_row_by_id_function(Editor)
update_manuscript_by_manuscript_id_and_editor_id = (
    update_table_row_by_id_and_foreign_key_function(Editor, Manuscript)
)


@blueprint.route("", methods=["GET"])
def index_endpoint():
    """
    Implements a GET /editors endpoint. All rows in the editors table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return display_editors()
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>", methods=["GET"])
def display_editor_by_id_endpoint(editor_id: int):
    """
    Implements a GET /editors/{editor_id} endpoint. The row in the editors table
    with the given editor_id is loaded and output in JSON.

    :editor_id: The editor_id of the row in the editors table to load and
                display.
    :return:    A flask.Response object.
    """
    try:
        return display_editor_by_id(editor_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/books", methods=["GET"])
def display_editor_books_endpoint(editor_id: int):
    """
    Implements a GET /editors/{editor_id}/books endpoint. All rows in the books
    table with that editor_id are loaded and output as a JSON list.

    :editor_id: The editor_id associated with book_ids in the
                editors_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    try:
        return display_books_by_editor_id(editor_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["GET"])
def display_editor_book_by_id_endpoint(editor_id: int, book_id: int):
    """
    Implements a GET /editors/{editor_id}/books/{book_id} endpoint. The row in
    the books table with that editor_id and that book_id is loaded and outputed
    in JSON.

    :editor_id: The editor_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    try:
        return display_book_by_book_id_and_editor_id(editor_id, book_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/manuscripts", methods=["GET"])
def display_editor_manuscripts_endpoint(editor_id: int):
    """
    Implements a GET /editors/{editor_id}/manuscripts endpoint. All rows in the
    manuscripts table with that editor_id are loaded and output as a JSON list.

    :editor_id: The editor_id associated with manuscript_ids in the
                editors_manuscripts table of rows from the manuscripts table to
                display.
    :return:    A flask.Response object.
    """
    try:
        return display_manuscripts_by_editor_id(editor_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["GET"])
def display_editor_manuscript_by_id_endpoint(editor_id: int, manuscript_id: int):
    """
    Implements a GET /editors/{editor_id}/manuscripts/{manuscript_id} endpoint.
    The row in the manuscripts table with that editor_id and that manuscript_id
    is loaded and outputed in JSON.

    :editor_id:       The editor_id of the row in the manuscripts table to
                      display.
    :manuscript_id:   The manuscript_id of the row in the manuscripts table to
                      load and display.
    :return:          A flask.Response object.
    """
    try:
        return display_manuscript_by_manuscript_id_and_editor_id(
            editor_id, manuscript_id
        )
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("", methods=["POST"])
def create_editor_endpoint():
    """
    Implements a POST /editors endpoint. A new row in the editors table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        check_json_req_props(Editor, request.json, {"editor_id"})
        return create_editor(request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>", methods=["PATCH", "PUT"])
def update_editor_by_id_endpoint(editor_id: int):
    """
    Implements a PATCH /editors/{editor_id} endpoint. The row in the editors
    table with that editor_id is updated from the JSON parameters.

    :editor_id: The editor_id of the row in the editors table to update.
    :return:    A flask.Response object.
    """
    try:
        return update_editor_by_id(editor_id, request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["PATCH", "PUT"])
def update_editor_book_by_id_endpoint(editor_id: int, book_id: int):
    """
    Implements a PATCH /editors/{editor_id}/books/{book_id} endpoint. The row
    in the books table with that book_id and that editor_id is updated from the
    JSON parameters.

    :editor_id: The editor_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        return update_book_by_book_id_and_editor_id(editor_id, book_id, request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route(
    "/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["PATCH", "PUT"]
)
def update_editor_manuscript_by_id_endpoint(editor_id: int, manuscript_id: int):
    """
    Implements a PATCH /editors/{editor_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id and that
    editor_id is updated from the JSON parameters.

    :editor_id:     The editor_id of the row in the manuscripts table to update.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    try:
        return update_manuscript_by_manuscript_id_and_editor_id(
            editor_id, manuscript_id, request.json
        )
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>", methods=["DELETE"])
def delete_editor_by_id_endpoint(editor_id: int):
    """
    Implements a DELETE /editors/{editor_id} endpoint. The row in the editors
    table with that editor_id is deleted.

    :editor_id: The editor_id of the row in the editors table to delete.
    :return:    A flask.Response object.
    """
    try:
        return delete_editor_by_id(editor_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["DELETE"])
def delete_editor_book_by_id_endpoint(editor_id: int, book_id: int):
    """
    Implements a DELETE /editors/{editor_id}/books/{book_id} endpoint. The row
    in the books table with that book_id and that editor_id is deleted.

    :editor_id: The editor_id of the row in the books table to delete.
    :book_id:   The book_id of the row in the books table to delete.
    :return:    A flask.Response object.
    """
    try:
        return delete_book_by_book_id_and_editor_id(editor_id, book_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["DELETE"])
def delete_editor_manuscript_by_id_endpoint(editor_id: int, manuscript_id: int):
    """
    Implements a DELETE /editors/{editor_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id and that
    editor_id is deleted.

    :editor_id:     The editor_id of the row in the manuscripts table to delete.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    try:
        return delete_manuscript_by_manuscript_id_and_editor_id(
            editor_id, manuscript_id
        )
    except Exception as exception:
        return handle_exception(exception)
