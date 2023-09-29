#!/usr/bin/python3

from flask import Blueprint, request, jsonify

from risuspubl.api.utility import (
    check_json_req_props,
    crt_tbl_row_clos,
    del_tbl_row_by_id_foreign_key_clos,
    del_tbl_row_by_id_clos,
    disp_tbl_row_by_id_foreign_key_clos,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_by_foreign_id_clos,
    disp_tbl_rows_clos,
    handle_exc,
    updt_tbl_row_by_id_foreign_key_clos,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import Book, Editor, Manuscript, db


blueprint = Blueprint("editors", __name__, url_prefix="/editors")


# These functions return closures that implement endpoint functions,
# filling in the blank(s) with the provided class objects.


# A closure for GET /editors
disp_edtrs = disp_tbl_rows_clos(Editor)

# A closure for POST /editors
crt_edtr = crt_tbl_row_clos(Editor)


# A closure for GET /editors/<id>
disp_edtr_by_id = disp_tbl_row_by_id_clos(Editor)

# A closure for PATCH /editors/<id>
updt_edtr_by_id = updt_tbl_row_by_id_clos(Editor)

# A closure for DELETE /editors/<id>
del_edtr_by_id = del_tbl_row_by_id_clos(Editor)


# A closure for GET /editors/<id>/books
disp_bks_by_edtr_id = disp_tbl_rows_by_foreign_id_clos(Editor, "editor_id", Book)


# A closure for GET /editors/<id>/books/<id>
disp_bk_by_bkid_and_edtr_id = disp_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Book, "book_id"
)

# A closure for PATCH /editors/<id>/books/<id>
updt_bk_by_bkid_and_edtr_id = updt_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Book, "book_id"
)

# A closure for DELETE /editors/<id>/books/<id>
del_bk_by_bkid_and_edtr_id = del_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Book, "book_id"
)


# A closure for GET /editors/<id>/manuscripts
disp_mscrpts_by_edtr_id = disp_tbl_rows_by_foreign_id_clos(
    Editor, "editor_id", Manuscript
)


# A closure for GET /editors/<id>/manuscripts/<id>
disp_mscrpt_by_msid_and_edtr_id = disp_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Manuscript, "manuscript_id"
)

# A closure for PATCH /editors/<id>/manuscripts/<id>
updt_mscrpt_by_msid_and_edtr_id = updt_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Manuscript, "manuscript_id"
)

# A closure for DELETE /editors/<id>/manuscripts/<id>
del_mscrpt_by_msid_and_edtr_id = del_tbl_row_by_id_foreign_key_clos(
    Editor, "editor_id", Manuscript, "manuscript_id"
)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /editors endpoint. All rows in the editors table
    are loaded and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        return disp_edtrs()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>", methods=["GET"])
def disp_edtr_by_edid_endpt(editor_id: int):
    """
    Implements a GET /editors/{editor_id} endpoint. The row in the
    editors table with the given editor_id is loaded and output in JSON.

    :editor_id: The editor_id of the row in the editors table to load
    and display.
    :return: A flask.Response object.
    """
    try:
        return disp_edtr_by_id(editor_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/books", methods=["GET"])
def disp_edtr_bks_endpt(editor_id: int):
    """
    Implements a GET /editors/{editor_id}/books endpoint. All rows in
    the books table with that editor_id are loaded and output as a JSON
    list.

    :editor_id: The editor_id associated with book_ids in the
    editors_books table of rows from the books table to display.
    :return: A flask.Response object.
    """
    try:
        return disp_bks_by_edtr_id(editor_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["GET"])
def disp_edtr_bk_by_edid_endpt(editor_id: int, book_id: int):
    """
    Implements a GET /editors/{editor_id}/books/{book_id} endpoint.
    The row in the books table with that editor_id and that book_id is
    loaded and outputed in JSON.

    :editor_id: The editor_id of the row in the books table to display.
    :book_id: The book_id of the row in the books table to load and
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_bk_by_bkid_and_edtr_id(editor_id, book_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/manuscripts", methods=["GET"])
def disp_edtr_mscrpts_endpt(editor_id: int):
    """
    Implements a GET /editors/{editor_id}/manuscripts endpoint. All rows
    in the manuscripts table with that editor_id are loaded and output
    as a JSON list.

    :editor_id: The editor_id associated with manuscript_ids in the
    editors_manuscripts table of rows from the manuscripts table to
    display.
    :return: A flask.Response object.
    """
    try:
        return disp_mscrpts_by_edtr_id(editor_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["GET"])
def disp_edtr_mscrpt_by_edid_endpt(editor_id: int, manuscript_id: int):
    """
    Implements a GET /editors/{editor_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that editor_id and
    that manuscript_id is loaded and outputed in JSON.

    :editor_id: The editor_id of the row in the manuscripts table to
    display.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to load and display.
    :return: A flask.Response object.
    """
    try:
        return disp_mscrpt_by_msid_and_edtr_id(editor_id, manuscript_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["POST"])
def crt_edtr_endpt():
    """
    Implements a POST /editors endpoint. A new row in the editors table
    is constituted from the JSON parameters and saved to that table.

    :return: A flask.Response object.
    """
    try:
        check_json_req_props(Editor, request.json, {"editor_id"})
        return crt_edtr(request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>", methods=["PATCH", "PUT"])
def updt_edtr_by_edid_endpt(editor_id: int):
    """
    Implements a PATCH /editors/{editor_id} endpoint. The row in
    the editors table with that editor_id is updated from the JSON
    parameters.

    :editor_id: The editor_id of the row in the editors table to update.
    :return: A flask.Response object.
    """
    try:
        return updt_edtr_by_id(editor_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["PATCH", "PUT"])
def updt_edtr_bk_by_edid_endpt(editor_id: int, book_id: int):
    """
    Implements a PATCH /editors/{editor_id}/books/{book_id} endpoint.
    The row in the books table with that book_id and that editor_id is
    updated from the JSON parameters.

    :editor_id: The editor_id of the row in the books table to update.
    :book_id: The book_id of the row in the books table to update.
    :return: A flask.Response object.
    """
    try:
        if not len(request.json):
            raise ValueError(
                "update action executed with no parameters indicating "
                + "fields to update"
            )
        check_json_req_props(Book, request.json, {"book_id"}, chk_missing=False)
        return updt_bk_by_bkid_and_edtr_id(editor_id, book_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["PATCH", "PUT"]
)
def updt_edtr_mscrpt_by_edid_endpt(editor_id: int, manuscript_id: int):
    """
    Implements a PATCH /editors/{editor_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    and that editor_id is updated from the JSON parameters.

    :editor_id: The editor_id of the row in the manuscripts table to
    update.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to update.
    :return: A flask.Response object.
    """
    try:
        if not len(request.json):
            raise ValueError(
                "update action executed with no parameters indicating "
                + "fields to update"
            )
        check_json_req_props(
            Manuscript, request.json, {"manuscript_id"}, chk_missing=False
        )
        return updt_mscrpt_by_msid_and_edtr_id(editor_id, manuscript_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>", methods=["DELETE"])
def del_edtr_by_edid_endpt(editor_id: int):
    """
    Implements a DELETE /editors/{editor_id} endpoint. The row in the
    editors table with that editor_id is deleted. All rows in the books
    and manuscripts tables that have editor_id set equal to that value
    have it reset to null.

    :editor_id: The editor_id of the row in the editors table to delete.
    :return: A flask.Response object.
    """
    try:
        # Checking for the existence of this Editor object
        editor_obj = Editor.query.get_or_404(editor_id)

        # Finding all Book and Manuscript objects with the editor_id
        # column set to this value and resetting it to None i.e. null
        book_objs = Book.query.filter(Book.editor_id == editor_id)
        for book_obj in book_objs:
            book_obj.editor_id = None
        manuscript_objs = Manuscript.query.filter(Manuscript.editor_id == editor_id)
        for manuscript_obj in manuscript_objs:
            manuscript_obj.editor_id = None
        db.session.commit()

        # Deleting the object, now free of foreign key dependencies
        db.session.delete(editor_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/books/<int:book_id>", methods=["DELETE"])
def del_edtr_bk_by_edid_endpt(editor_id: int, book_id: int):
    """
    Implements a DELETE /editors/{editor_id}/books/{book_id} endpoint.
    The row in the books table with that book_id and that editor_id is
    deleted.

    :editor_id: The editor_id of the row in the books table to delete.
    :book_id: The book_id of the row in the books table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_bk_by_bkid_and_edtr_id(editor_id, book_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:editor_id>/manuscripts/<int:manuscript_id>", methods=["DELETE"])
def del_edtr_mscrpt_by_edid_endpt(editor_id: int, manuscript_id: int):
    """
    Implements a DELETE /editors/{editor_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    and that editor_id is deleted.


    :editor_id: The editor_id of the row in the manuscripts table to
    delete.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to delete.
    :return: A flask.Response object.
    """
    try:
        return del_mscrpt_by_msid_and_edtr_id(editor_id, manuscript_id)
    except Exception as exception:
        return handle_exc(exception)
