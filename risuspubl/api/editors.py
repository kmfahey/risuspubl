#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('editors', __name__, url_prefix='/editors')


editor_update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                 'last_name': (str, (), request.args.get('last_name')),
                                 'salary': (int, (), request.args.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [editor_obj.serialize() for editor_obj in Editor.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['GET'])
def show_editor(editor_id: int):
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


@blueprint.route('', methods=['POST'])
def create_editor():
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


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor(editor_id: int):
    try:
        delete_model_obj(editor_id, Editor)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>/books/<int:book_id>', methods=['DELETE'])
def delete_editor_book_by_id(editor_id: int, book_id: int):
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

