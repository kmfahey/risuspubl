#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import create_class_obj_factory, delete_class_obj_by_id_factory, \
        delete_one_classes_other_class_obj_by_id_factory, show_all_of_one_classes_other_class_objs, show_class_index, \
        show_class_obj_by_id, show_one_classes_other_class_obj_by_id, update_class_obj_by_id_factory, \
        update_one_classes_other_class_obj_by_id_factory
from risuspubl.dbmodels import Book, Editor, Manuscript


blueprint = Blueprint('editors', __name__, url_prefix='/editors')


# These are callable objects being instanced from classes imported from
# risuspubl.api.utility. See that module for the classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
editor_book_by_id_deleter = delete_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Book, 'book_id')
editor_book_by_id_shower = show_one_classes_other_class_obj_by_id(Editor, 'editor_id', Book, 'book_id')
editor_book_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Book, 'book_id')
editor_books_shower = show_all_of_one_classes_other_class_objs(Editor, 'editor_id', Book)
editor_by_id_deleter = delete_class_obj_by_id_factory(Editor, 'editor_id')
editor_by_id_shower = show_class_obj_by_id(Editor)
editor_by_id_updater = update_class_obj_by_id_factory(Editor, 'editor_id')
editor_creator = create_class_obj_factory(Editor)
editor_manuscript_by_id_deleter = delete_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Manuscript,
                                                                                   'manuscript_id')
editor_manuscript_by_id_shower = show_one_classes_other_class_obj_by_id(Editor, 'editor_id', Manuscript,
                                                                        'manuscript_id')
editor_manuscript_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Manuscript,
                                                                                   'manuscript_id')
editor_manuscripts_shower = show_all_of_one_classes_other_class_objs(Editor, 'editor_id', Manuscript)
editors_indexer = show_class_index(Editor)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /editors endpoint. All rows in the editors table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return editors_indexer()


@blueprint.route('/<int:editor_id>', methods=['GET'])
def show_editor_by_id(editor_id: int):
    """
    Implements a GET /editors/<id> endpoint. The row in the editors table with
    the given editor_id is loaded and output in JSON.

    :editor_id: The editor_id of the row in the editors table to load and
                display.
    :return:    A flask.Response object.
    """
    return editor_by_id_shower(editor_id)


@blueprint.route('/<int:editor_id>/books', methods=['GET'])
def show_editor_books(editor_id: int):
    """
    Implements a GET /editors/<id>/books endpoint. All rows in the books table
    with that editor_id are loaded and output as a JSON list.

    :editor_id: The editor_id associated with book_ids in the
                editors_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    return editor_books_shower(editor_id)


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['GET'])
def show_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a GET /editors/<id>/books/<id> endpoint. The row in the books
    table with that editor_id and that book_id is loaded and outputed in JSON.

    :editor_id: The editor_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    return editor_book_by_id_shower(editor_id, book_id)


@blueprint.route('/<int:editor_id>/manuscripts', methods=['GET'])
def show_editor_manuscripts(editor_id: int):
    """
    Implements a GET /editors/<id>/manuscripts endpoint. All rows in the
    manuscripts table with that editor_id are loaded and output as a JSON list.

    :editor_id: The editor_id associated with manuscript_ids in the
                editors_manuscripts table of rows from the manuscripts table to
                display.
    :return:    A flask.Response object.
    """
    return editor_manuscripts_shower(editor_id)


@blueprint.route('/<int:editor_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_editor_manuscript_by_id(editor_id: int, manuscript_id: int):
    """
    Implements a GET /editors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that editor_id and that manuscript_id is loaded and
    outputed in JSON.

    :editor_id:       The editor_id of the row in the manuscripts table to
                      display.
    :manuscript_id:   The manuscript_id of the row in the manuscripts table to
                      load and display.
    :return:          A flask.Response object.
    """
    return editor_manuscript_by_id_shower(editor_id, manuscript_id)


@blueprint.route('', methods=['POST'])
def create_editor():
    """
    Implements a POST /editors endpoint. A new row in the editors table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return editor_creator(request.json)


@blueprint.route('/<int:editor_id>', methods=['PATCH', 'PUT'])
def update_editor_by_id(editor_id: int):
    """
    Implements a PATCH /editors/<id> endpoint. The row in the editors table with
    that editor_id is updated from the JSON parameters.

    :editor_id: The editor_id of the row in the editors table to update.
    :return:    A flask.Response object.
    """
    return editor_by_id_updater(editor_id, request.json)


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['PATCH', 'PUT'])
def update_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a PATCH /editors/<id>/books/<id> endpoint. The row in the
    books table with that book_id and that editor_id is updated from the JSON
    parameters.

    :editor_id: The editor_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    return editor_book_by_id_updater(editor_id, book_id, request.json)


@blueprint.route('/<int:editor_id>/manuscripts/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_editor_manuscript_by_id(editor_id: int, manuscript_id: int):
    """
    Implements a PATCH /editors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that editor_id is updated from
    the JSON parameters.

    :editor_id:     The editor_id of the row in the manuscripts table to update.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    return editor_manuscript_by_id_updater(editor_id, manuscript_id, request.json)


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor_by_id(editor_id: int):
    """
    Implements a DELETE /editors/<id> endpoint. The row in the editors table
    with that editor_id is deleted.

    :editor_id: The editor_id of the row in the editors table to delete.
    :return:    A flask.Response object.
    """
    return editor_by_id_deleter(editor_id)


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['DELETE'])
def delete_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a DELETE /editors/<id>/books/<id> endpoint. The row in the books
    table with that book_id and that editor_id is deleted.

    :editor_id: The editor_id of the row in the books table to delete.
    :book_id:   The book_id of the row in the books table to delete.
    :return:    A flask.Response object.
    """
    return editor_book_by_id_deleter(editor_id, book_id)


@blueprint.route('/<int:editor_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_editor_manuscript_by_id(editor_id: int, manuscript_id: int):
    """
    Implements a DELETE /editors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that editor_id is deleted.

    :editor_id:     The editor_id of the row in the manuscripts table to delete.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    return editor_manuscript_by_id_deleter(editor_id, manuscript_id)
