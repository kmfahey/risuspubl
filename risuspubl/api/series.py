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
    """
    Implements a GET /series endpoint. All rows in the series table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    try:
        result = [series_obj.serialize() for series_obj in Series.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series(series_id: int):
    """
    Implements a GET /series/<id> endpoint. The row in the series table with
    the given series_id is loaded and output in JSON.

    :series_id: The series_id of the row in the series table to load and
                display.
    :return:    A flask.Response object.
    """
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
    """
    Implements a GET /series/<id>/books endpoint. All rows in the books table
    with that series_id are loaded and output as a JSON list.

    :series_id: The series_id associated with book_ids in the
                series_books table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    try:
        Series.query.get_or_404(series_id)
        # A Book object for every row in the books table with the given
        # series_id.
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
    """
    Implements a GET /series/<id>/books/<id> endpoint. The row in the books
    table with that series_id and that book_id is loaded and outputed in JSON.

    :series_id: The series_id of the row in the books table to display.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    try:
        Series.query.get_or_404(series_id)
        # A Book object for every row in the books table with the given series_id.
        book_objs = list(Book.query.where(Book.series_id == series_id))
        # Iterating across the list looking for the Book object with the given
        # manuscript_id. If it's found, it's serialized and returned. Otherwise,
        # a 404 error is raised.
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
    try:
        Series.query.get_or_404(series_id)
        # A Manuscript object for every row in the manuscripts table with the
        # given series_id.
        retval = [manuscript_obj.serialize() for manuscript_obj
                  in Manuscript.query.where(Manuscript.series_id == series_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


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
    try:
        Series.query.get_or_404(series_id)
        # A Manuscript object for every row in the manuscripts table with the given series_id.
        manuscript_objs = list(Manuscript.query.where(Manuscript.series_id == series_id))
        # Iterating across the list looking for the Manuscript object with the
        # given manuscript_id. If it's found, it's serialized and returned.
        # Otherwise, a 404 error is raised.
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
def create_series():
    """
    Implements a POST /series endpoint. A new row in the series table is
    constituted from the CGI parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        # Using create_model_obj() to process request.args into a Series()
        # argument dict and instance a Series() object.
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
    """
    Implements a PATCH /series/<id> endpoint. The row in the series table with
    that series_id is updated from the CGI parameters.

    :series_id: The series_id of the row in the series table to update.
    :return:    A flask.Response object.
    """
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
    """
    Implements a PATCH /series/<id>/books/<id> endpoint. The row in the
    books table with that book_id and that series_id is updated from the CGI
    parameters.

    :series_id: The series_id of the row in the books table to update.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        Series.query.get_or_404(series_id)
        # Confirming that there's a row in the books table with the given
        # book_id and series_id.
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.series_id == series_id)):
            return abort(404)
        # Using update_model_obj() to fetch the book_obj and update it
        # against request.args.
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


@blueprint.route('/<int:series_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_series_manuscript_by_id(series_id: int, manuscript_id: int):
    """
    Implements a PATCH /series/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that series_id is updated from the CGI
    parameters.

    :series_id: The series_id of the row in the manuscripts table to update.
    :manuscript_id:   The manuscript_id of the row in the manuscripts table to update.
    :return:    A flask.Response object.
    """
    try:
        Series.query.get_or_404(series_id)
        # Confirming that there's a row in the manuscripts table with the given
        # manuscript_id and series_id.
        if not any(manuscript_obj.manuscript_id == manuscript_id for manuscript_obj
                   in Manuscript.query.where(Manuscript.series_id == series_id)):
            return abort(404)
        # Using update_model_obj() to fetch the manuscript_obj and update it
        # against request.args.
        manuscript_obj = update_model_obj(manuscript_id, Manuscript,
                                          {'series_id':        (int,  (0,),    request.args.get('series_id')),
                                           'series_id':        (int,  (0,),    series_id),
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


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    """
    Implements a DELETE /series/<id> endpoint. The row in the series table
    with that series_id is deleted.

    :series_id: The series_id of the row in the series table to delete.
    :return:    A flask.Response object.
    """
    try:
        delete_model_obj(series_id, Series)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>/books/<int:book_id>', methods=['DELETE'])
def delete_series_book_by_id(series_id: int, book_id: int):
    """
    Implements a DELETE /series/<id>/books/<id> endpoint. The row in the books
    table with that book_id and that series_id is deleted.

    :series_id: The series_id of the row in the books table to delete.
    :book_id:   The book_id of the row in the books table to delete.
    :return:    A flask.Response object.
    """
    try:
        series_obj = Series.query.get_or_404(series_id)
        # Confirming that there's a row in the books table with the given
        # book_id and series_id.
        if not any(book_obj.book_id == book_id for book_obj in Book.query.where(Book.series_id == series_id)):
            return abort(404)
        # Using delete_model_obj() to fetch the book_obj and delete it.
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


@blueprint.route('/<int:series_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_series_manuscript_by_id(series_id: int, manuscript_id: int):
    """
    Implements a DELETE /series/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id and that series_id is deleted.

    :series_id:     The series_id of the row in the manuscripts table to delete.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    try:
        series_obj = Series.query.get_or_404(series_id)
        # Confirming that there's a row in the manuscripts table with the given
        # series_id and manuscript_id.
        if not any(manuscript_obj.manuscript_id == manuscript_id for manuscript_obj
                   in Manuscript.query.where(Manuscript.series_id == series_id)):
            return abort(404)
        # Using delete_model_obj() to fetch the series_obj and delete it.
        delete_model_obj(manuscript_id, Manuscript)
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
