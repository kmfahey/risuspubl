#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('series', __name__, url_prefix='/series')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Series class. By wrapping it in a
# zero-argument lambda, the embedded request.args variable isn't evaluated until
# the function is called within the context of an endpoint function.
update_or_create_args = lambda: {'title': (str, (), request.args.get('title')),
                                 'volumes': (int, (2, 5), request.args.get('volumes'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [series_obj.serialize() for series_obj in Series.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series(series_id: int):
    try:
        series_obj = Series.query.get_or_404(series_id)
        return jsonify(series_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>/books', methods=['GET'])
def show_series_books(series_id: int):
    try:
        Series.query.get_or_404(series_id)
        retval = [book_obj.serialize() for book_obj in Book.query.where(Book.series_id == series_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['GET'])
def show_series_book_by_id(series_id: int, book_id: int):
    try:
        Series.query.get_or_404(series_id)
        book_objs = list(Book.query.where(Book.series_id == series_id))
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
def create_series():
    try:
        series_obj = create_model_obj(Series, update_or_create_args())
        db.session.add(series_obj)
        db.session.commit()
        return jsonify(series_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['PATCH'])
def update_series(series_id: int):
    try:
        series_obj = update_model_obj(series_id, Series, update_or_create_args())
        db.session.add(series_obj)
        db.session.commit()
        return jsonify(series_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['PATCH'])
def update_series_book_by_id(series_id: int, book_id: int):
    try:
        Series.query.get_or_404(series_id)
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.series_id == series_id)):
            return abort(404)
        book_obj = update_model_obj(book_id, Book,
                                    {'series_id':        (int,  (0,),    request.args.get('series_id')),
                                     'series_id':        (int,  (0,),    series_id),
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


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    try:
        delete_model_obj(series_id, Series)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['DELETE'])
def delete_series_book_by_id(series_id: int, book_id: int):
    try:
        series_obj = Series.query.get_or_404(series_id)
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.series_id == series_id)):
            return abort(404)
        delete_model_obj(book_id, Book)
        series_obj.volumes = series_obj.volumes - 1
        db.session.add(series_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
