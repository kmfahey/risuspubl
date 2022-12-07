#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools

from werkzeug.exceptions import NotFound

from datetime import date, timedelta

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('authors', __name__, url_prefix='/authors')


create_or_update_author = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                   'last_name': (str, (), request.args.get('last_name'))}

create_or_update_book = lambda: {'editor_id': (int, (0,), request.args.get('editor_id')),
                                 'series_id': (int, (0,), request.args.get('series_id')),
                                 'title': (str, (), request.args.get('title')),
                                 'publication_date': (str, (), request.args.get('publication_date')),
                                 'edition_number': (str, (1, 10), request.args.get('edition_number')),
                                 'is_in_print': (bool, (), request.args.get('is_in_print'))}

create_or_update_manuscript = lambda: {'editor_id': (int, (0,), request.args.get('editor_id')),
                                       'series_id': (int, (0,), request.args.get('series_id')),
                                       'working_title': (str, (), request.args.get('working_title')),
                                       'due_date': (date, ((date.today() + timedelta(days=1)).isoformat(),
                                                           "2023-07-01"),
                                                    request.args.get('due_date')),
                                       'advance': (int, (5000, 100000), request.args.get('advance'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [author_obj.serialize() for author_obj in Author.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>', methods=['GET'])
def show_author(author_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        return jsonify(author_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/books', methods=['GET'])
def show_author_books(author_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [book_obj.serialize() for book_obj in author_obj.books]
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['GET'])
def show_author_book_by_id(author_id: int, book_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        for book_obj in author_obj.books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        return Response(f'author with author_id {author_id} does not have a book with book_id {book_id}', status=400)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/manuscripts', methods=['GET'])
def show_author_manuscripts(author_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [manuscript_obj.serialize() for manuscript_obj in author_obj.manuscripts]
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_author_manuscript_by_id(author_id: int, manuscript_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        for manuscript_obj in author_obj.manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>', methods=['GET'])
def show_authors(author1_id: int, author2_id: int):
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        retval = [author1_obj.serialize(), author2_obj.serialize()]
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


def _authors_shared_book_ids(author1_id: int, author2_id: int) -> set:
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        author1_books = author1_obj.books
        author2_books = author2_obj.books
        book_objs_by_id = {book_obj.book_id: book_obj for book_obj in itertools.chain(author1_books, author2_books)}
        shared_book_ids = set(author1_book_obj.book_id for author1_book_obj in author1_books) & \
                              set(author2_book_obj.book_id for author2_book_obj in author2_books)
        return [book_objs_by_id[book_id] for book_id in shared_book_ids]
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['GET'])
def show_authors_books(author1_id: int, author2_id: int):
    try:
        shared_books = _authors_shared_book_ids(author1_id, author2_id)
        retval = [book_obj.serialize() for book_obj in shared_books]
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['GET'])
def show_authors_book_by_id(author1_id: int, author2_id: int, book_id: int):
    try:
        shared_books = _authors_shared_book_ids(author1_id, author2_id)
        for book_obj in shared_books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


def _authors_shared_manuscript_ids(author1_id: int, author2_id: int) -> set:
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        author1_manuscripts = author1_obj.manuscripts
        author2_manuscripts = author2_obj.manuscripts
        manuscript_objs_by_id = {manuscript_obj.manuscript_id: manuscript_obj for manuscript_obj
                                 in itertools.chain(author1_manuscripts, author2_manuscripts)}
        shared_manuscript_ids = set(author1_manuscript_obj.manuscript_id
                                    for author1_manuscript_obj in author1_manuscripts) & \
                              set(author2_manuscript_obj.manuscript_id
                                  for author2_manuscript_obj in author2_manuscripts)
        return [manuscript_objs_by_id[manuscript_id] for manuscript_id in shared_manuscript_ids]
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['GET'])
def show_authors_manuscripts(author1_id: int, author2_id: int):
    try:
        shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
        retval = [manuscript_obj.serialize() for manuscript_obj in shared_manuscripts]
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_authors_manuscript_by_id(author1_id: int, author2_id: int, manuscript_id: int):
    try:
        shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
        for manuscript_obj in shared_manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_author():
    try:
        author_obj = create_model_obj(Author, create_or_update_author())
        db.session.add(author_obj)
        db.session.commit()
        return jsonify(author_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/books', methods=['POST'])
def create_author_book(author_id: int):
    try:
        Author.query.get_or_404(author_id)
        book_obj = create_model_obj(Book, create_or_update_book(), optional_params={'series_id'})
        db.session.add(book_obj)
        db.session.commit()
        ab_insert = Authors_Books.insert().values(author_id=author_id, book_id=book_obj.book_id)
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['POST'])
def create_authors_book(author1_id: int, author2_id: int):
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        book_obj = create_model_obj(Book, create_or_update_book(), optional_params={'series_id'})
        db.session.add(book_obj)
        db.session.commit()
        ab1_insert = Authors_Books.insert().values(author_id=author1_id, book_id=book_obj.book_id)
        ab2_insert = Authors_Books.insert().values(author_id=author2_id, book_id=book_obj.book_id)
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/manuscripts', methods=['POST'])
def create_author_manuscript(author_id: int):
    try:
        Author.query.get_or_404(author_id)
        manuscript_obj = create_model_obj(Manuscript, create_or_update_manuscript(), optional_params={'series_id'})
        db.session.add(manuscript_obj)
        db.session.commit()
        ab_insert = Authors_Manuscripts.insert().values(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['POST'])
def create_authors_manuscript(author1_id: int, author2_id: int):
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        manuscript_obj = create_model_obj(Manuscript, create_or_update_manuscript(), optional_params={'series_id'})
        db.session.add(manuscript_obj)
        db.session.commit()
        ab1_insert = Authors_Manuscripts.insert().values(author_id=author1_id,
                                                         manuscript_id=manuscript_obj.manuscript_id)
        ab2_insert = Authors_Manuscripts.insert().values(author_id=author2_id,
                                                         manuscript_id=manuscript_obj.manuscript_id)
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>', methods=['PATCH'])
def update_author(author_id: int):
    try:
        author_obj = update_model_obj(author_id, Author, create_or_update_author())
        db.session.add(author_obj)
        db.session.commit()
        return jsonify(author_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['PATCH'])
def update_author_book(author_id: int, book_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        if len(book_objs) == 0:
            return abort(404)
        book_obj = update_model_obj(book_id, Book, create_or_update_book())
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['PATCH'])
def update_authors_book(author1_id: int, author2_id: int, book_id: int):
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author1_obj.books))
        a2_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author2_obj.books))
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        book_obj = update_model_obj(book_id, Book, create_or_update_book())
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_author_manuscript(author_id: int, manuscript_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts))
        if len(manuscript_objs) == 0:
            return abort(404)
        manuscript_obj = update_model_obj(manuscript_id, Manuscript, create_or_update_manuscript())
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author1_obj.manuscripts))
        a2_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author2_obj.manuscripts))
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)
        manuscript_obj = update_model_obj(manuscript_id, Manuscript, create_or_update_manuscript())
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        ab_del = Authors_Books.delete().where(Authors_Books.columns[0] == author_id)
        db.session.execute(ab_del)
        am_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[0] == author_id)
        db.session.execute(am_del)
        db.session.commit()
        db.session.delete(author_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['DELETE'])
def delete_author_book(author_id: int, book_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        if len(book_objs) == 0:
            return abort(404)
        book_obj, = book_objs
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['DELETE'])
def delete_authors_book(author1_id: int, author2_id: int, book_id: int):
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author1_obj.books))
        a2_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author2_obj.books))
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        book_obj, = a1_book_objs
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_author_manuscript(author_id: int, manuscript_id: int):
    try:
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts))
        if len(manuscript_objs) == 0:
            return abort(404)
        manuscript_obj, = manuscript_objs
        ab_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author1_obj.manuscripts))
        a2_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author2_obj.manuscripts))
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)
        manuscript_obj, = a1_manuscript_objs
        ab_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
