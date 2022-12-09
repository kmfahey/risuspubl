#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.endpfact import delete_class_obj_by_id_factory, show_class_index, show_class_obj_by_id, \
        update_class_obj_by_id_factory
from risuspubl.dbmodels import Book


blueprint = Blueprint('books', __name__, url_prefix='/books')


# These are callable objects being instanced from classes imported from
# risuspubl.api.endpfact. See that module for the classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
book_by_id_deleter = delete_class_obj_by_id_factory(Book, 'book_id')
book_by_id_shower = show_class_obj_by_id(Book)
book_by_id_updater = update_class_obj_by_id_factory(Book, 'book_id')
books_indexer = show_class_index(Book)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /books endpoint. All rows in the books table are loaded
    and output as a JSON list.

    :return:    A flask.Response object.
    """
    return books_indexer()


@blueprint.route('/<int:book_id>', methods=['GET'])
def show_book_by_id(book_id: int):
    """
    Implements a GET /books/<id> endpoint. The row in the books table with the
    given book_id is loaded and output in JSON.

    :book_id: The book_id of the row in the books table to load and
              display.
    :return:  A flask.Response object.
    """
    return book_by_id_shower(book_id)


# A Create endpoint is deliberately not implemented, because without
# a way to specify the author or authors to attach the book to, no
# entry in the authors_books table would be created and the book
# would an orphan in the database. /authors/<author_id>/books and
# /authors/<author1_id>/<author2_id>/books already accept Create actions and
# when done that way associations with an author or authors can be created
# appropriately.


@blueprint.route('/<int:book_id>', methods=['PATCH', 'PUT'])
def update_book_by_id(book_id: int):
    """
    Implements a PATCH /books/<id> endpoint. The row in the books table with
    that book_id is updated from the JSON parameters.

    :book_id: The book_id of the row in the books table to update.
    :return:  A flask.Response object.
    """
    return book_by_id_updater(book_id, request.json)


@blueprint.route('/<int:book_id>', methods=['DELETE'])
def delete_book_by_id(book_id: int):
    """
    Implements a DELETE /books/<id> endpoint. The row in the books table with
    that book_id is deleted.

    :book_id: The book_id of the row in the books table to delete.
    :return:  A flask.Response object.
    """
    return book_by_id_deleter(book_id)
