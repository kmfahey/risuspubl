#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools
import re

from flask import Blueprint, jsonify, request, Response, abort

from risuspubl.dbmodels import *
from risuspubl.api.commons import *



blueprint = Blueprint('authors', __name__, url_prefix='/authors')


# decorator takes path and list of HTTP verbs
@blueprint.route('', methods=['GET'])
def index():
    # ORM performs SELECT query
    result = [author_obj.serialize() for author_obj in Author.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:author_id>', methods=['GET'])
def show_author(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    return jsonify(author_obj.serialize())


@blueprint.route('/<int:author_id>/books', methods=['GET'])
def show_author_books(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    retval = [book_obj.serialize() for book_obj in author_obj.books]
    return jsonify(retval)


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['GET'])
def show_author_book_by_id(author_id: int, book_id: int):
    author_obj = Author.query.get_or_404(author_id)
    for book_obj in author_obj.books:
        if book_obj.book_id != book_id:
            continue
        return jsonify(book_obj.serialize())
    return Response(f'author with author_id {author_id} does not have a book with book_id {book_id}', status=400)


@blueprint.route('/<int:author_id>/manuscripts', methods=['GET'])
def show_author_manuscripts(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    retval = [manuscript_obj.serialize() for manuscript_obj in author_obj.manuscripts]
    return jsonify(retval)


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_author_manuscript_by_id(author_id: int, manuscript_id: int):
    author_obj = Author.query.get_or_404(author_id)
    for manuscript_obj in author_obj.manuscripts:
        if manuscript_obj.manuscript_id != manuscript_id:
            continue
        return jsonify(manuscript_obj.serialize())
    return abort(404)


@blueprint.route('/<int:author1_id>/<int:author2_id>', methods=['GET'])
def show_authors(author1_id: int, author2_id: int):
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    retval = [author1_obj.serialize(), author2_obj.serialize()]
    return jsonify(retval)


def _authors_shared_book_ids(author1_id: int, author2_id: int) -> set:
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    author1_books = author1_obj.books
    author2_books = author2_obj.books
    book_objs_by_id = {book_obj.book_id: book_obj for book_obj in itertools.chain(author1_books, author2_books)}
    shared_book_ids = set(author1_book_obj.book_id for author1_book_obj in author1_books) & \
                          set(author2_book_obj.book_id for author2_book_obj in author2_books)
    return [book_objs_by_id[book_id] for book_id in shared_book_ids]


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['GET'])
def show_authors_books(author1_id: int, author2_id: int):
    shared_books = _authors_shared_book_ids(author1_id, author2_id)
    retval = [book_obj.serialize() for book_obj in shared_books]
    return jsonify(retval)


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['GET'])
def show_authors_book_by_id(author1_id: int, author2_id: int, book_id: int):
    shared_books = _authors_shared_book_ids(author1_id, author2_id)
    for book_obj in shared_books:
        if book_obj.book_id != book_id:
            continue
        return jsonify(book_obj.serialize())
    return abort(404)


def _authors_shared_manuscript_ids(author1_id: int, author2_id: int) -> set:
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


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['GET'])
def show_authors_manuscripts(author1_id: int, author2_id: int):
    shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
    retval = [manuscript_obj.serialize() for manuscript_obj in shared_manuscripts]
    return jsonify(retval)


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_authors_manuscript_by_id(author1_id: int, author2_id: int, manuscript_id: int):
    shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
    for manuscript_obj in shared_manuscripts:
        if manuscript_obj.manuscript_id != manuscript_id:
            continue
        return jsonify(manuscript_obj.serialize())
    return abort(404)


@blueprint.route('', methods=['POST'])
def create_author():
    author_args = dict()
    try:
        author_args['first_name'] = validate_str(request.args['first_name'])
        author_args['last_name'] = validate_str(request.args['last_name'])
    except:
        return abort(400)
    author_obj = Author(**author_args)
    db.session.add(author_obj)
    db.session.commit()
    return jsonify(author_obj.serialize())


def _validate_book_args():
    book_args = dict()
    try:
        if Editor.query.get(request_args['editor_id']) is None:
            return abort(400)
        book_args['editor_id'] = validate_int(request.args['editor_id'], 0)
        if 'series_id' in request.args:
            if Series.query.get(request_args['series_id']) is None:
                return abort(400)
            book_args['series_id'] = validate_int(request.args['series_id'], 0)
        if len(tuple(Book.query.where(Book.title == book_args['title']))):
            raise ValueError()
        book_args['title'] = validate_str(request.args['title'])
        book_args['publication_date'] = validate_date(request.args['publication_date'])
        book_args['edition_number'] = validate_int(request.args['edition_number'], 1, 10)
        book_args['is_in_print'] = False if request.args['is_in_print'] in ("0", "false", "False") else True
    except:
        return abort(400)
    return book_args


@blueprint.route('/<int:author_id>/books', methods=['POST'])
def create_author_book(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    book_args = _validate_book_args()
    book_obj = Book(**book_args)
    db.session.add(book_obj)
    db.session.commit()
    ab_insert = Authors_Books.insert().values(author_id=author_id, book_id=book_obj.book_id)
    db.session.execute(ab_insert)
    db.session.commit()
    return jsonify(book_obj.serialize())


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['POST'])
def create_authors_book(author1_id: int, author2_id: int):
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    book_args = _validate_book_args()
    book_obj = Book(**book_args)
    db.session.add(book_obj)
    db.session.commit()
    ab1_insert = Authors_Books.insert().values(author_id=author1_id, book_id=book_obj.book_id)
    ab2_insert = Authors_Books.insert().values(author_id=author2_id, book_id=book_obj.book_id)
    db.session.execute(ab1_insert)
    db.session.execute(ab2_insert)
    db.session.commit()
    return jsonify(book_obj.serialize())


def _validate_manuscript_args():
    manuscript_args = dict()
    try:
        if Editor.query.get(request_args['editor_id']) is None:
            return abort(400)
        manuscript_args['editor_id'] = validate_int(request.args['editor_id'], 0)
        if 'series_id' in request.args:
            if Series.query.get(request_args['series_id']) is None:
                return abort(400)
            manuscript_args['series_id'] = validate_int(request.args['series_id'], 0)
        if len(tuple(Manuscript.query.where(Manuscript.working_title == manuscript_args['working_title']))):
            raise ValueError()
        manuscript_args['working_title'] = validate_str(request.args['working_title'])
        manuscript_args['due_date'] = validate_date(request.args['due_date'])
        manuscript_args['advance'] = validate_int(request.args['advance'], 1000, 100000)
    except:
        return abort(400)
    return manuscript_args


@blueprint.route('/<int:author_id>/manuscripts', methods=['POST'])
def create_author_manuscript(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    manuscript_args = _validate_manuscript_args()
    manuscript_obj = Manuscript(**manuscript_args)
    db.session.add(manuscript_obj)
    db.session.commit()
    ab_insert = Authors_Manuscripts.insert().values(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
    db.session.execute(ab_insert)
    db.session.commit()
    return jsonify(manuscript_obj.serialize())


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['POST'])
def create_authors_manuscript(author1_id: int, author2_id: int):
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    manuscript_args = _validate_manuscript_args()
    manuscript_obj = Manuscript(**manuscript_args)
    db.session.add(manuscript_obj)
    db.session.commit()
    ab1_insert = Authors_Manuscripts.insert().values(author_id=author1_id, manuscript_id=manuscript_obj.manuscript_id)
    ab2_insert = Authors_Manuscripts.insert().values(author_id=author2_id, manuscript_id=manuscript_obj.manuscript_id)
    db.session.execute(ab1_insert)
    db.session.execute(ab2_insert)
    db.session.commit()
    return jsonify(manuscript_obj.serialize())


@blueprint.route('/<int:author_id>', methods=['PATCH'])
def update_author(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    if 'first_name' in request.args:
        author_obj.first_name = validate_str(request.args['first_name'])
    if 'second_name' in request.args:
        author_obj.last_name = validate_str(request.args['last_name'])
    db.session.add(author_obj)
    db.session.commit()
    return jsonify(author_obj.serialize())


def _update_book_obj(book_obj):
    if 'editor_id' in request.args:
        if Editor.query.get(request_args['editor_id']) is None:
            return abort(400)
        book_obj.editor_id = validate_int(request.args['editor_id'], 0)
    if 'series_id' in request.args:
        if Series.query.get(request_args['series_id']) is None:
            return abort(400)
        book_obj.series_id = validate_int(request.args['series_id'], 0)
    if 'title' in request.args:
        if len(tuple(Book.query.where(Book.title == request.args['title']))):
            raise ValueError()
        book_obj.title = validate_str(request.args['title'])
    if 'publication_date' in request.args:
        book_obj.publication_date = validate_date(request.args['publication_date'])
    if 'edition_number' in request.args:
        book_obj.edition_number = validate_int(request.args['edition_number'], 1, 10)
    if 'is_in_print' in request.args:
        book_obj.is_in_print = False if request.args['is_in_print'] in ("0", "false", "False") else True
    return book_obj


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['PATCH'])
def update_author_book(author_id: int, book_id: int):
    author_obj = Author.query.get_or_404(author_id)
    book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
    if len(book_objs) == 0:
        return abort(404)
    book_obj = _update_book_obj(book_objs[0])
    db.session.add(book_obj)
    db.session.commit()
    return jsonify(book_obj.serialize())


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['PATCH'])
def update_authors_book(author1_id: int, author2_id: int, book_id: int):
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    a1_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author1_obj.books))
    a2_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author2_obj.books))
    if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
        return abort(404)
    book_obj = _update_book_obj(a1_book_objs[0])
    db.session.add(book_obj)
    db.session.commit()
    return jsonify(book_obj.serialize())


def _update_manuscript_obj(manuscript_obj):
    if 'editor_id' in request.args:
        if Editor.query.get(request_args['editor_id']) is None:
            return abort(400)
        manuscript_obj.editor_id = validate_int(request.args['editor_id'], 0)
    if 'series_id' in request.args:
        if Series.query.get(request_args['series_id']) is None:
            return abort(400)
        manuscript_obj.series_id = validate_int(request.args['series_id'], 0)
    if 'working_title' in request.args:
        if len(tuple(Manuscript.query.where(Manuscript.working_title == request.args['working_title']))):
            raise ValueError()
        manuscript_obj.working_title = validate_str(request.args['working_title'])
    if 'due_date' in request.args:
        manuscript_obj.due_date = validate_date(request.args['due_date'])
    if 'advance' in request.args:
        manuscript_obj.advance = validate_int(request.args['advance'], 5000, 100000)
    return manuscript_obj


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_author_manuscript(author_id: int, manuscript_id: int):
    author_obj = Author.query.get_or_404(author_id)
    manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts))
    if len(manuscript_objs) == 0:
        return abort(404)
    manuscript_obj = _update_manuscript_obj(manuscript_objs[0])
    db.session.add(manuscript_obj)
    db.session.commit()
    return jsonify(manuscript_obj.serialize())


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['PATCH'])
def update_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    a1_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author1_obj.manuscripts))
    a2_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author2_obj.manuscripts))
    if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
        return abort(404)
    manuscript_obj = _update_manuscript_obj(a1_manuscript_objs[0])
    db.session.add(manuscript_obj)
    db.session.commit()
    return jsonify(manuscript_obj.serialize())


@blueprint.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id: int):
    author_obj = Author.query.get_or_404(author_id)
    ab_del = Authors_Books.delete().where(Authors_Books.columns[0] == author_id)
    db.session.execute(ab_del)
    am_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[0] == author_id)
    db.session.execute(am_del)
    db.session.commit()
    db.session.delete(author_obj)
    db.session.commit()
    return jsonify(True)


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['DELETE'])
def delete_author_book(author_id: int, book_id: int):
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


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['DELETE'])
def delete_authors_book(author1_id: int, author2_id: int, book_id: int):
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


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_author_manuscript(author_id: int, manuscript_id: int):
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


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
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
