#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from datetime import date

from flask import Blueprint, Response, abort, jsonify, request

from werkzeug.exceptions import NotFound

from risuspubl.api.commons import create_model_obj, delete_model_obj, update_model_obj
from risuspubl.api.endpfact import delete_one_classes_other_class_obj_by_id_factory, delete_class_obj_by_id_factory, \
        update_one_classes_other_class_obj_by_id_factory, update_class_obj_by_id_factory, create_class_obj_factory, \
        show_one_classes_other_class_obj_by_id
from risuspubl.dbmodels import Book, Editor, Manuscript, db

blueprint = Blueprint('editors', __name__, url_prefix='/editors')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Editor class. By wrapping it in a
# zero-argument lambda, the embedded request.json variable isn't evaluated until
# the function is called within the context of an endpoint function.
editor_update_or_create_args = lambda: {'first_name':   (str,   (),     request.json.get('first_name')),
                                        'last_name':    (str,   (),     request.json.get('last_name')),
                                        'salary':       (int,   (),     request.json.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /editors endpoint. All rows in the editors table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        result = [editor_obj.serialize() for editor_obj in Editor.query.all()]
        return jsonify(result)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['GET'])
def show_editor(editor_id: int):
    """
    Implements a GET /editors/<id> endpoint. The row in the editors table with
    the given editor_id is loaded and output in JSON.

    :editor_id: The editor_id of the row in the editors table to load and
                display.
    :return:    A flask.Response object.
    """
    try:
        editor_obj = Editor.query.get_or_404(editor_id)
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/books', methods=['GET'])
def show_editor_books(editor_id: int):
    """
    Implements a GET /editors/<id>/books endpoint. All rows in the books table
    with that editor_id are loaded and output as a JSON list.

    :editor_id: The editor_id associated with book_ids in the
                editors_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    try:
        Editor.query.get_or_404(editor_id)
        # A Book object for every row in the manuscripts table with the
        # given value for editor_id.
        retval = [book_obj.serialize() for book_obj in Book.query.where(Book.editor_id == editor_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


editor_book_by_id_shower = show_one_classes_other_class_obj_by_id(Editor, 'editor_id', Book, 'book_id')



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
    try:
        Editor.query.get_or_404(editor_id)
        # A Manuscript object for every row in the manuscripts table with the
        # given value for editor_id.
        retval = [manuscript_obj.serialize() for manuscript_obj
                  in Manuscript.query.where(Manuscript.editor_id == editor_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


editor_manuscript_by_id_shower = show_one_classes_other_class_obj_by_id(Editor, 'editor_id', Manuscript,
                                                                        'manuscript_id')


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


editor_creator = create_class_obj_factory(Editor)


@blueprint.route('', methods=['POST'])
def create_editor():
    """
    Implements a POST /editors endpoint. A new row in the editors table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return editor_creator(request.json)


editor_by_id_updater = update_class_obj_by_id_factory(Editor, 'editor_id')


@blueprint.route('/<int:editor_id>', methods=['PATCH', 'PUT'])
def update_editor_by_id(editor_id: int):
    """
    Implements a PATCH /editors/<id> endpoint. The row in the editors table with
    that editor_id is updated from the JSON parameters.

    :editor_id: The editor_id of the row in the editors table to update.
    :return:    A flask.Response object.
    """
    return editor_by_id_updater(editor_id, request.json)


editor_book_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Book, 'book_id')


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


editor_manuscript_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Editor, 'editor_id', Manuscript, 'manuscript_id')


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


editor_by_id_deleter = delete_class_obj_by_id_factory(Editor, 'editor_id')


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor(editor_id: int):
    """
    Implements a DELETE /editors/<id> endpoint. The row in the editors table
    with that editor_id is deleted.

    :editor_id: The editor_id of the row in the editors table to delete.
    :return:    A flask.Response object.
    """
    return editor_by_id_deleter(editor_id)


editor_book_by_id_deleter = delete_one_classes_other_class_obj_by_id_factory(
                                Editor, 'editor_id', Book, 'book_id')


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


editor_manuscript_by_id_deleter = delete_one_classes_other_class_obj_by_id_factory(
                                       Editor, 'editor_id', Manuscript, 'manuscript_id')


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
