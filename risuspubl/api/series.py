#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import sys, pprint

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.api.endpfact import delete_one_classes_other_class_obj_by_id_factory, \
        update_one_classes_other_class_obj_by_id_factory, delete_class_obj_by_id_factory, \
        update_class_obj_by_id_factory, create_class_obj_factory, show_one_classes_other_class_obj_by_id, \
        show_all_of_one_classes_other_class_objs, show_class_index, show_class_obj_by_id

from risuspubl.dbmodels import *


blueprint = Blueprint('series', __name__, url_prefix='/series')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Series class. By wrapping it in a
# zero-argument lambda, the embedded request.json variable isn't evaluated until
# the function is called within the context of an endpoint function.
update_or_create_args = lambda: {'title':   (str,   (),     request.json.get('title')),
                                 'volumes': (int,   (2, 5), request.json.get('volumes'))}


series_indexer = show_class_index(Series)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /series endpoint. All rows in the series table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return series_indexer()


series_by_id_shower = show_class_obj_by_id(Series)


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series_by_id(series_id: int):
    """
    Implements a GET /series/<id> endpoint. The row in the series table with
    the given series_id is loaded and output in JSON.

    :series_id: The series_id of the row in the series table to load and
                display.
    :return:    A flask.Response object.
    """
    return series_by_id_shower(series_id)


series_books_shower = show_all_of_one_classes_other_class_objs(Series, 'series_id', Book)


@blueprint.route('/<int:series_id>/books', methods=['GET'])
def show_series_books(series_id: int):
    """
    Implements a GET /series/<id>/books endpoint. All rows in the books table
    with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with book_ids in the
                series_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    return series_books_shower(series_id)


series_book_by_id_shower = show_one_classes_other_class_obj_by_id(Series, 'series_id', Book, 'book_id')


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['GET'])
def show_series_book_by_id(series_id: int, book_id: int):
    """
    Implements a GET /series/<id>/books/<id> endpoint. The row in the books
    table with that series_id and that book_id is loaded and outputed in JSON.

    :series_id: The series_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    return series_book_by_id_shower(series_id, book_id)


series_manuscripts_shower = show_all_of_one_classes_other_class_objs(Series, 'series_id', Manuscript)


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
    return series_manuscripts_shower(series_id)


series_manuscript_by_id_shower = show_one_classes_other_class_obj_by_id(Series, 'series_id', Manuscript,
                                                                        'manuscript_id')


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
    return series_manuscript_by_id_shower(series_id, manuscript_id)


series_creator = create_class_obj_factory(Series)


@blueprint.route('', methods=['POST'])
def create_series():
    """
    Implements a POST /series endpoint. A new row in the series table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return series_creator(request.json)


series_by_id_updater = update_class_obj_by_id_factory(Series, 'series_id')


@blueprint.route('/<int:series_id>', methods=['PATCH', 'PUT'])
def update_series_by_id(series_id: int):
    """
    Implements a PATCH /series/<id> endpoint. The row in the series table with
    that series_id is updated from the JSON parameters.

    :series_id: The series_id of the row in the series table to update.
    :return:    A flask.Response object.
    """
    return series_by_id_updater(series_id, request.json)


series_book_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Series, 'series_id', Book, 'book_id')


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
    return series_book_by_id_updater(series_id, book_id, request.json)


series_manuscript_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Series, 'series_id',
                                                                                   Manuscript, 'manuscript_id')


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
    return series_manuscript_by_id_updater(series_id, manuscript_id, request.json)


series_by_id_deleter = delete_class_obj_by_id_factory(Series, 'series_id')


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    """
    Implements a DELETE /series/<id> endpoint. The row in the series table
    with that series_id is deleted.

    :series_id: The series_id of the row in the series table to delete.
    :return:    A flask.Response object.
    """
    return series_by_id_deleter(series_id)
