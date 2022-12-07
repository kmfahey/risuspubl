#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from datetime import date

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('books', __name__, url_prefix='/books')


@blueprint.route('', methods=['GET'])
def index():
    result = [book_obj.serialize() for book_obj in Book.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:book_id>', methods=['GET'])
def show_book(book_id: int):
    book_obj = Book.query.get_or_404(book_id)
    return jsonify(book_obj.serialize())


# A Create endpoint is deliberately not implemented, because without
# a way to specify the author or authors to attach the book to, no
# entry in the authors_books table would be created and the book
# would an orphan in the database. /authors/<author_id>/books and
# /authors/<author1_id>/<author2_id>/books already accept Create actions and
# when done that way associations with an author or authors can be created
# appropriately.


@blueprint.route('/<int:book_id>', methods=['PATCH'])
def update_book(book_id: int):
    try:
        if 'title' in request.args:
            if len(tuple(Book.query.where(Book.title == request.args['title']))):
                raise ValueError(f"'title' parameter value '{request.args['title']}' already use in a row in the "
                                 f'{Book.__tablename__} table; title values must be unique')
        book_obj = update_model_obj(book_id, Book,
                                    {'editor_id':        (int,  (0,),    request.args.get('editor_id')),
                                     'series_id':        (int,  (0,),    request.args.get('series_id')),
                                     'title':            (str,  (),      request.args.get('title')),
                                     'publication_date': (date, (),      request.args.get('publication_date')),
                                     'edition_number':   (int,  (1, 10), request.args.get('edition_number')),
                                     'is_in_print':      (bool, (),      request.args.get('is_in_print'))})
    except ValueError as exception:
        return Response(exception.args[0], status=400) if len(exception.args) else abort(400)
    db.session.add(book_obj)
    db.session.commit()
    return jsonify(book_obj.serialize())


@blueprint.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int):
    delete_model_obj(book_id, Book)
    return jsonify(True)
