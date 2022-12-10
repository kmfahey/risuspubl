#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import create_table_row, delete_table_row_by_id, display_table_row_by_id, \
        display_table_row_by_id_and_foreign_key, display_table_rows, display_table_rows_by_foreign_id, \
        update_table_row_by_id, update_table_row_by_id_and_foreign_key
from risuspubl.dbmodels import Book, Manuscript, Series


blueprint = Blueprint('series', __name__, url_prefix='/series')


# These are callable objects-- functions with state-- instanced from
# risuspubl.api.utility.endpoint_action subclasses. See that module for the
# classes. Each implements a common design pattern in the endpoint functions
# this package implements.
create_series = create_table_row(Series)
delete_series_by_id = delete_table_row_by_id(Series)
display_book_by_book_id_and_series_id = display_table_row_by_id_and_foreign_key(Series, Book)
display_books_by_series_id = display_table_rows_by_foreign_id(Series, Book)
display_manuscript_by_manuscript_id_and_series_id = display_table_row_by_id_and_foreign_key(Series, Manuscript)
display_manuscripts_by_series_id = display_table_rows_by_foreign_id(Series, Manuscript)
display_series_by_id = display_table_row_by_id(Series)
display_series = display_table_rows(Series)
update_book_by_book_id_and_series_id = update_table_row_by_id_and_foreign_key(Series, Book)
update_manuscript_by_manuscript_id_and_series_idr = update_table_row_by_id_and_foreign_key(Series, Manuscript)
update_series_by_id = update_table_row_by_id(Series)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /series endpoint. All rows in the series table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return display_series()


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series_by_id(series_id: int):
    """
    Implements a GET /series/<id> endpoint. The row in the series table with
    the given series_id is loaded and output in JSON.

    :series_id: The series_id of the row in the series table to load and
                display.
    :return:    A flask.Response object.
    """
    return display_series_by_id(series_id)


@blueprint.route('/<int:series_id>/books', methods=['GET'])
def show_series_books(series_id: int):
    """
    Implements a GET /series/<id>/books endpoint. All rows in the books table
    with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with book_ids in the
                series_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    return display_books_by_series_id(series_id)


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['GET'])
def show_series_book_by_id(series_id: int, book_id: int):
    """
    Implements a GET /series/<id>/books/<id> endpoint. The row in the books
    table with that series_id and that book_id is loaded and outputed in JSON.

    :series_id: The series_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    return display_book_by_book_id_and_series_id(series_id, book_id)


@blueprint.route('/<int:series_id>/manuscripts', methods=['GET'])
def show_series_manuscripts(series_id: int):
    """
    Implements a GET /series/<id>/manuscripts endpoint. All rows in the
    manuscripts table with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with manuscript_ids in the
                series_manuscripts table of rows from the manuscripts table to
                display.
    :return:    A flask.Response object.
    """
    return display_manuscripts_by_series_id(series_id)


@blueprint.route('/<int:series_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_series_manuscript_by_id(series_id: int, manuscript_id: int):
    """
    Implements a GET /series/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that series_id and that manuscript_id is loaded and
    outputed in JSON.

    :series_id:     The series_id of the row in the manuscripts table to
                    display.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    return display_manuscript_by_manuscript_id_and_series_id(series_id, manuscript_id)


@blueprint.route('', methods=['POST'])
def create_series():
    """
    Implements a POST /series endpoint. A new row in the series table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return create_series(request.json)


@blueprint.route('/<int:series_id>', methods=['PATCH', 'PUT'])
def update_series_by_id(series_id: int):
    """
    Implements a PATCH /series/<id> endpoint. The row in the series table with
    that series_id is updated from the JSON parameters.

    :series_id: The series_id of the row in the series table to update.
    :return:    A flask.Response object.
    """
    return update_series_by_id(series_id, request.json)


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['PATCH', 'PUT'])
def update_series_book_by_id(series_id: int, book_id: int):
    """
    Implements a PATCH /series/<id>/books/<id> endpoint. The row in the
    books table with that book_id and that series_id is updated from the JSON
    parameters.

    :series_id: The series_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    return update_book_by_book_id_and_series_id(series_id, book_id, request.json)


@blueprint.route('/<int:series_id>/manuscripts/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_series_manuscript_by_id(series_id: int, manuscript_id: int):
    """
    Implements a PATCH /series/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that series_id is updated from the JSON
    parameters.

    :series_id: The series_id of the row in the manuscripts table to update.
    :manuscript_id:   The manuscript_id of the row in the manuscripts table to update.
    :return:    A flask.Response object.
    """
    return update_manuscript_by_manuscript_id_and_series_idr(series_id, manuscript_id, request.json)


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series_by_id(series_id: int):
    """
    Implements a DELETE /series/<id> endpoint. The row in the series table
    with that series_id is deleted.

    :series_id: The series_id of the row in the series table to delete.
    :return:    A flask.Response object.
    """
    return delete_series_by_id(series_id)
