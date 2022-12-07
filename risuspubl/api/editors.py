#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('editors', __name__, url_prefix='/editors')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Editor class. By wrapping it in a
# zero-argument lambda, the embedded request.args variable isn't evaluated until
# the function is called within the context of an endpoint function.
editor_update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                 'last_name': (str, (), request.args.get('last_name')),
                                 'salary': (int, (), request.args.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /editors endpoint. All rows in the editors table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        result = [editor_obj.serialize() for editor_obj in Editor.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
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
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
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
        retval = [book_obj.serialize() for book_obj in Book.query.where(Book.editor_id == editor_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['GET'])
def show_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a GET /editors/<id>/books/<id> endpoint. The row in the books
    table with that editor_id and that book_id is loaded and outputed in JSON.

    :editor_id: The editor_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    try:
        Editor.query.get_or_404(editor_id)
        book_objs = list(Book.query.where(Book.editor_id == editor_id))
        for book_obj in book_objs:
            if book_obj.book_id == book_id:
                return jsonify(book_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


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
        retval = [manuscript_obj.serialize() for manuscript_obj
                  in Manuscript.query.where(Manuscript.editor_id == editor_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


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
    try:
        Editor.query.get_or_404(editor_id)
        manuscript_objs = list(Manuscript.query.where(Manuscript.editor_id == editor_id))
        for manuscript_obj in manuscript_objs:
            if manuscript_obj.manuscript_id == manuscript_id:
                return jsonify(manuscript_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_editor():
    """
    Implements a POST /editors endpoint. A new row in the editors table is
    constituted from the CGI parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        editor_obj = create_model_obj(Editor, editor_update_or_create_args())
        db.session.add(editor_obj)
        db.session.commit()
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['PATCH'])
def update_editor(editor_id: int):
    """
    Implements a PATCH /editors/<id> endpoint. The row in the editors table with
    that editor_id is updated from the CGI parameters.

    :editor_id: The editor_id of the row in the editors table to update.
    :return:    A flask.Response object.
    """
    try:
        editor_obj = update_model_obj(editor_id, Editor, editor_update_or_create_args())
        db.session.add(editor_obj)
        db.session.commit()
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['PATCH'])
def update_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a PATCH /editors/<id>/books/<id> endpoint. The row in the
    books table with that book_id and that editor_id is updated from the CGI
    parameters.

    :editor_id: The editor_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        Editor.query.get_or_404(editor_id)
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.editor_id == editor_id)):
            return abort(404)
        book_obj = update_model_obj(book_id, Book,
                                    {'editor_id':        (int,  (0,),    editor_id),
                                     'series_id':        (int,  (0,),    request.args.get('series_id')),
                                     'title':            (str,  (),      request.args.get('title')),
                                     'publication_date': (date, (),      request.args.get('publication_date')),
                                     'edition_number':   (int,  (1, 10), request.args.get('edition_number')),
                                     'is_in_print':      (bool, (),      request.args.get('is_in_print'))})
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_editor_manuscript_by_id(editor_id: int, manuscript_id: int):
    """
    Implements a PATCH /editors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that editor_id is updated from
    the CGI parameters.

    :editor_id:     The editor_id of the row in the manuscripts table to update.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    try:
        Editor.query.get_or_404(editor_id)
        if not any(manuscript_obj.manuscript_id == manuscript_id for manuscript_obj
                   in Manuscript.query.where(Manuscript.editor_id == editor_id)):
            return abort(404)
        manuscript_obj = update_model_obj(manuscript_id, Manuscript,
                                    {'editor_id':        (int,  (0,),    editor_id),
                                     'series_id':        (int,  (0,),    request.args.get('series_id')),
                                     'title':            (str,  (),      request.args.get('title')),
                                     'publication_date': (date, (),      request.args.get('publication_date')),
                                     'edition_number':   (int,  (1, 10), request.args.get('edition_number')),
                                     'is_in_print':      (bool, (),      request.args.get('is_in_print'))})
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor(editor_id: int):
    """
    Implements a DELETE /editors/<id> endpoint. The row in the editors table
    with that editor_id is deleted.

    :editor_id: The editor_id of the row in the editors table to delete.
    :return:    A flask.Response object.
    """
    try:
        delete_model_obj(editor_id, Editor)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['DELETE'])
def delete_editor_book_by_id(editor_id: int, book_id: int):
    """
    Implements a DELETE /editors/<id>/books/<id> endpoint. The row in the books
    table with that book_id and that editor_id is deleted.

    :editor_id: The editor_id of the row in the books table to delete.
    :book_id:   The book_id of the row in the books table to delete.
    :return:    A flask.Response object.
    """
    try:
        Editor.query.get_or_404(editor_id)
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.editor_id == editor_id)):
            return abort(404)
        delete_model_obj(book_id, Book)
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


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
    try:
        Editor.query.get_or_404(editor_id)
        if not any(manuscript_obj.manuscript_id == manuscript_id for manuscript_obj
                   in Manuscript.query.where(Manuscript.editor_id == editor_id)):
            return abort(404)
        delete_model_obj(manuscript_id, Manuscript)
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))

