#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools

from flask import Blueprint, Response, abort, jsonify, request

import werkzeug.exceptions

from risuspubl.api.utility import create_table_row, create_model_obj, create_or_update_argd_gen, \
        display_table_row_by_id, display_table_rows, endpoint_action, update_model_obj, \
        update_table_row_by_id
from risuspubl.dbmodels import Author, Authors_Books, Authors_Manuscripts, Book, Manuscript, db


blueprint = Blueprint('authors', __name__, url_prefix='/authors')


# These are callable objects-- basically functions with state-- being instanced
# from classes imported from risuspubl.api.utility. See that module for the
# classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
create_author = create_table_row(Author)
display_author_by_id = display_table_row_by_id(Author)
display_authors = display_table_rows(Author)
update_author_by_id = update_table_row_by_id(Author, 'author_id')

# risuspubl.api.authors is the one module where the majority of endpoint
# functions are not handled using .api.utility classes. Because of the
# Author model class's unique relationship with the Authors_Manuscripts and
# Authors_Books table classes, and this endpoint's support for dual author_ids,
# most of its endpoint functions have unique implementations that don't
# generalize.


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /authors endpoint. All rows in the authors table are loaded
    and output as a JSON list.

    :return:    A flask.Response object.
    """
    return display_authors()


@blueprint.route('/<int:author_id>', methods=['GET'])
def show_author_by_id(author_id: int):
    """
    Implements a GET /authors/<id> endpoint. The row in the authors table with
    the given author_id is loaded and output in JSON.

    :author_id: The author_id of the row in the authors table to load and
                display.
    :return:    A flask.Response object.
    """
    return display_author_by_id(author_id)


@blueprint.route('/<int:author_id>/books', methods=['GET'])
def show_author_books(author_id: int):
    """
    Implements a GET /authors/<id>/books endpoint. All rows in the books table
    associated with that author_id in the authors_books table are loaded and
    output as a JSON list.

    :author_id: The author_id associated with book_ids in the authors_books
                table of rows from the books table to display.
    :return:    A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [book_obj.serialize() for book_obj in author_obj.books]
        return jsonify(retval)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['GET'])
def show_author_book_by_id(author_id: int, book_id: int):
    """
    Implements a GET /authors/<id>/books/<id> endpoint. The row in the books
    table with that book_id associated with that author_id in the authors_books
    table is loaded and outputed in JSON.

    :author_id: The author_id associated with the given book_id in the
                authors_books table.
    :book_id:   The book_id of the row in the books table to load and display.
    :return:    A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        # Iterating across the Author.manuscripts list looking for a Book object
        # by that id. If it's found, it's serialized and returned as JSON.
        # Otherwise, a 404 error is raised.
        for book_obj in author_obj.books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        return Response(f'author with author_id {author_id} does not have a book with book_id {book_id}', status=400)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/manuscripts', methods=['GET'])
def show_author_manuscripts(author_id: int):
    """
    Implements a GET /authors/<id>/manuscripts endpoint. All rows in the
    manuscripts table associated with that author_ids in the authors_manuscripts
    table are loaded and output as a JSON list.

    :author_id: The author_id associated with manuscript_ids in the
                authors_manuscripts table of rows from the manuscripts table to
                display.
    :return:    A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [manuscript_obj.serialize() for manuscript_obj in author_obj.manuscripts]
        return jsonify(retval)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_author_manuscript_by_id(author_id: int, manuscript_id: int):
    """
    Implements a GET /authors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id associated with that author_id in
    the authors_manuscripts table is loaded and outputed in JSON.

    :author_id:     The author_id associated with the given manuscript_id in
                    the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        # Iterating across the Author.manuscripts list looking for a Manuscript
        # object by that id. If it's found, it's serialized and returned as
        # JSON. Otherwise, a 404 error is raised.
        for manuscript_obj in author_obj.manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        return abort(404)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


# To be frank this endpoint doesn't have much of a reason to exist, save that
# if this endpoint is loaded something *should* be here since /authors/<id> is
# valid and /authors/<id>/<id>/books is valid. Provied for completeness.
@blueprint.route('/<int:author1_id>/<int:author2_id>', methods=['GET'])
def show_authors_by_ids(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/<id>/<id> endpoint. The rows in the authors table
    with those two author_ids are loaded and outputed in a JSON list.

    :author1_id: One of the two author_ids of rows in the authors table to
                 load and display.
    :author2_id: The other of the two author_ids of rows in the authors table
                 to load and display.
    :return:     A flask.Response object.
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        # The two author_objs are serialized and returned as a 2-element json
        # list.
        retval = [author1_obj.serialize(), author2_obj.serialize()]
        return jsonify(retval)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


# This private utility function is used by show_authors_books() and
# show_authors_book_by_id() to generate a list of Book objects with book_ids
# that are associated with both author_ids in the authors_books table.
def _authors_shared_book_ids(author1_id: int, author2_id: int) -> set:
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    # The books attribute on an Author object comprises the Book
    # objects whose book_ids are associated with its author_id in the
    # authors_books table.
    author1_books = author1_obj.books
    author2_books = author2_obj.books
    # A dict of Book objects by book_id is built from both lists
    # chained in sequence.
    book_objs_by_id = {book_obj.book_id: book_obj for book_obj in itertools.chain(author1_books, author2_books)}
    # Sets of book_ids associated with each author_id are built and
    # intersected to find the shared books.
    shared_book_ids = set(author1_book_obj.book_id for author1_book_obj in author1_books) & \
                          set(author2_book_obj.book_id for author2_book_obj in author2_books)
    # The book_ids are looked up in the dict via a list comprehension and
    # that list is returned.
    return [book_objs_by_id[book_id] for book_id in shared_book_ids]


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['GET'])
def show_authors_books(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/<id>/<id>/books endpoint. All rows in the books
    table associated with those two author_ids in the authors_books table are
    loaded and output as a JSON list.

    :author1_id: One of the two author_ids associated with matching book_ids
                 in the authors_books table.
    :author2_id: The other of the two author_ids associated with matching
                 book_ids in the authors_books table.
    :return:     A flask.Response object.
    """
    try:
        # A utility function is used to fetch a list of Book objects whose
        # book_id is associated with both author_ids in authors_books.
        shared_books = _authors_shared_book_ids(author1_id, author2_id)
        # The list is serialized and returned as json.
        retval = [book_obj.serialize() for book_obj in shared_books]
        return jsonify(retval)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['GET'])
def show_authors_book_by_id(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a GET /authors/<id>/<id>/books/<id> endpoint. The row in the
    books table with that book_id associated with those two author_ids in the
    authors_books table is loaded and outputed in JSON.

    :author1_id: One of the two author_ids associated with the given book_id
                 in the authors_books table.
    :author2_id: The other of the two author_ids associated with the given
                 book_id in the authors_books table.
    :book_id:    The book_id of the row in the books table to load and
                 display.
    :return:     A flask.Response object.
    """
    try:
        # A utility function is used to fetch a list of Book objects whose
        # book_id is associated with both author_ids in authors_books.
        shared_books = _authors_shared_book_ids(author1_id, author2_id)
        # The Book object list is iterated over, looking for the object with the
        # matching book_id. If it's found, it's serialized and returned as json.
        for book_obj in shared_books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        # If the book_id wasn't found, that's a 404.
        return abort(404)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


# This private utility function is used by show_authors_manuscripts()
# and show_authors_manuscript_by_id() to generate a list of Book objects
# with manuscript_ids that are associated with both author_ids in the
# authors_manuscripts table.
def _authors_shared_manuscript_ids(author1_id: int, author2_id: int) -> set:
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    # The manuscripts attribute on an Author object comprises the Manuscript
    # objects whose manuscript_ids are associated with its author_id in the
    # authors_manuscripts table.
    author1_manuscripts = author1_obj.manuscripts
    author2_manuscripts = author2_obj.manuscripts
    # A dict of Manuscript objects by manuscript_id is built from both lists
    # chained in sequence.
    manuscript_objs_by_id = {manuscript_obj.manuscript_id: manuscript_obj for manuscript_obj
                             in itertools.chain(author1_manuscripts, author2_manuscripts)}
    # Sets of manuscript_ids associated with each author_id are built and
    # intersected to find the shared manuscripts.
    shared_manuscript_ids = set(author1_manuscript_obj.manuscript_id
                                for author1_manuscript_obj in author1_manuscripts) & \
                          set(author2_manuscript_obj.manuscript_id
                              for author2_manuscript_obj in author2_manuscripts)
    # The manuscript_ids are looked up in the dict via a list comprehension and
    # that list is returned.
    return [manuscript_objs_by_id[manuscript_id] for manuscript_id in shared_manuscript_ids]


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['GET'])
def show_authors_manuscripts(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/<id>/<id>/manuscripts endpoint. All rows
    in the manuscripts table associated with those two author_ids in the
    authors_manuscripts table are loaded and output as a JSON list.

    :author1_id:    One of the two author_ids associated with matching
                    manuscript_ids in the authors_manuscripts table.
    :author2_id:    The other of the two author_ids associated with matching
                    manuscript_ids in the authors_manuscripts table.
    :return:        A flask.Response object.
    """
    try:
        # This utility function looks up which manuscript_ids are associated
        # with both author_ids in authors_manuscripts and returns Manuscript()
        # objects for those manuscript_ids.
        shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
        # A list of serializations is built # and returned via jsonify.
        retval = [manuscript_obj.serialize() for manuscript_obj in shared_manuscripts]
        return jsonify(retval)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['GET'])
def show_authors_manuscript_by_id(author1_id: int, author2_id: int, manuscript_id: int):
    """
    Implements a GET /authors/<id>/<id>/manuscripts/<id> endpoint. The row in
    the manuscripts table with that manuscript_id associated with those two
    author_ids in the authors_manuscripts table is loaded and outputed in JSON.

    :author1_id:    One of the two author_ids associated with the given
                    manuscript_id in the authors_manuscripts table.
    :author2_id:    The other of the two author_ids associated with the given
                    manuscript_id in the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    try:
        # Using a utility function to look up which manuscript_ids are
        # associated with both author_ids in authors_manuscripts and return
        # Manuscript() objects for those manuscript_ids.
        shared_manuscripts = _authors_shared_manuscript_ids(author1_id, author2_id)
        # Iterating across the Manuscript object list until the object with the
        # matching manuscript_id is found.
        for manuscript_obj in shared_manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        # If the loop completed and the Manuscript() object wasn't found, that's
        # a 404.
        return abort(404)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('', methods=['POST'])
def author_create():
    """
    Implements a POST /authors endpoint. A new row in the authors table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return create_author(request.json)


@blueprint.route('/<int:author_id>/books', methods=['POST'])
def create_author_book(author_id: int):
    """
    Implements a POST /authors/<id>/books endpoint. A new row in the
    books table is constituted from the JSON parameters and saved to that
    table. In addition, a row in the authors_books table associating the
    new book_id with that author_id is added.

    :author_id: The author_id to associate the new book_id with in the
                authors_books table.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        Author.query.get_or_404(author_id)
        # Using create_model_obj() to process request.json into a Book()
        # argument dict and instance a Book() object.
        book_obj = create_model_obj(Book, create_or_update_argd_gen(Book).generate_argd(request.json),
                                    optional_params={'series_id'})
        db.session.add(book_obj)
        db.session.commit()
        # Associating the new book_id with both author_ids in the
        # authors_books table.
        ab_insert = Authors_Books.insert().values(author_id=author_id, book_id=book_obj.book_id)
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/books', methods=['POST'])
def create_authors_book(author1_id: int, author2_id: int):
    """
    Implements a POST /authors/<id>/books endpoint. A new row in the books table
    is constituted from the JSON parameters and saved to that table. In addition,
    rows in the authors_books table associating the new book_id with
    those two author_ids are added.

    :author1_id: One of the two author_ids to associate the new book_id
                 with in the authors_books table.
    :author2_id: The other of the two author_ids to associate the new
                 book_id with in the authors_books table.
    :book_id:    The book_id of the row in the books table to update.
    :return:     A flask.Response object.
    """
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        # Using create_model_obj() to process request.json into a Book()
        # argument dict and instance a Book() object.
        book_obj = create_model_obj(Book, create_or_update_argd_gen(Book).generate_argd(request.json),
                                    optional_params={'series_id'})
        db.session.add(book_obj)
        db.session.commit()
        # Associating the new book_id with both author_ids in the authors_books
        # table.
        ab1_insert = Authors_Books.insert().values(author_id=author1_id, book_id=book_obj.book_id)
        ab2_insert = Authors_Books.insert().values(author_id=author2_id, book_id=book_obj.book_id)
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/manuscripts', methods=['POST'])
def create_author_manuscript(author_id: int):
    """
    Implements a POST /authors/<id>/manuscripts endpoint. A new row in the
    manuscripts table is constituted from the JSON parameters and saved to that
    table. In addition, a row in the authors_manuscripts table associating the
    new manuscript_id with that author_id is added.

    :author_id: The author_id to associate the new manuscript_id with in the
                authors_manuscripts table.
    :book_id:   The book_id of the row in the books table to update.
    :return:    A flask.Response object.
    """
    try:
        Author.query.get_or_404(author_id)
        # Using create_model_obj() to process request.json into a Manuscript()
        # argument dict and instance a Manuscript() object.
        manuscript_obj = create_model_obj(Manuscript, create_or_update_argd_gen(Manuscript).generate_argd(request.json),
                                          optional_params={'series_id'})
        db.session.add(manuscript_obj)
        db.session.commit()
        # Associating the new manuscript_id with the author_id in the
        # authors_manuscripts table.
        ab_insert = Authors_Manuscripts.insert().values(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts', methods=['POST'])
def create_authors_manuscript(author1_id: int, author2_id: int):
    """
    Implements a POST /authors/<id>/<id>/manuscripts endpoint. A new row in the
    manuscripts table is constituted from the JSON parameters and saved to that
    table. In addition, rows in the authors_manuscripts table associating the
    new manuscript_id with those two author_ids are added.

    :author1_id: One of the two author_ids to associate the new manuscript_id
                 with in the authors_manuscripts table.
    :author2_id: The other of the two author_ids to associate the new
                 manuscript_id with in the authors_manuscripts table.
    :book_id:    The book_id of the row in the books table to update.
    :return:     A flask.Response object.
    """
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        # Using create_model_obj() to process request.json into a Manuscript()
        # argument dict and instance a Manuscript() object.
        manuscript_obj = create_model_obj(Manuscript, create_or_update_argd_gen(Manuscript).generate_argd(request.json),
                                          optional_params={'series_id'})
        db.session.add(manuscript_obj)
        db.session.commit()
        # Associating the new manuscript_id with both author_ids in the
        # authors_manuscripts table.
        ab1_insert = Authors_Manuscripts.insert().values(author_id=author1_id,
                                                         manuscript_id=manuscript_obj.manuscript_id)
        ab2_insert = Authors_Manuscripts.insert().values(author_id=author2_id,
                                                         manuscript_id=manuscript_obj.manuscript_id)
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>', methods=['PATCH', 'PUT'])
def update_author_by_id(author_id: int):
    """
    Implements a PATCH /authors/<id> endpoint. The row in the authors table with
    that author_id is updated from the JSON parameters.

    :author_id: The author_id of the row in the authors table to update.
    :return:    A flask.Response object.
    """
    return update_author_by_id(author_id, request.json)


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['PATCH', 'PUT'])
def update_author_book(author_id: int, book_id: int):
    """
    Implements a PATCH /authors/<id>/books/<id> endpoint. The row in the books
    table with that book_id associated with that author_id in the authors_books
    table is updated from the JSON parameters.

    :author_id: The author_id associated with that book_id in the
                authors_books table.
    :book_id:   The book_id of the row in the books table to
                update.
    :return:    A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        # Verifying that this author_id is associated with this book_id in
        # authors_books.
        if len(book_objs) == 0:
            return abort(404)
        # Using update_model_obj() to fetch the Book object and update it
        # against request.json.
        book_obj = update_model_obj(book_id, Book, create_or_update_argd_gen(Book).generate_argd(request.json))
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['PATCH', 'PUT'])
def update_authors_book(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a PATCH /authors/<id>/<id>/books/<id> endpoint. The row in the
    books table with that book_id associated with those two author_ids in the
    authors_books table is updated from the JSON parameters.

    :author1_id: One of the two author_ids associated with that book_id in the
                 authors_books table.
    :author2_id: The other of the two author_ids associated with that book_id
                 in the authors_books table.
    :book_id:    The book_id of the row in the books table to update.
    :return:     A flask.Response object.
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author1_obj.books))
        a2_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author2_obj.books))
        # Verifying that both author_ids are associated with this book_id in
        # authors_books.
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        book_obj = update_model_obj(book_id, Book, create_or_update_argd_gen(Book).generate_argd(request.json))
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_author_manuscript(author_id: int, manuscript_id: int):
    """
    Implements a PATCH /authors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id associated with that author_id in
    the authors_manuscripts table is updated from the JSON parameters.

    :author_id:     The author_id associated with that manuscript_id in the
                    authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts))
        # Verifying that this author_id is associated with this manuscript_id in
        # authors_manuscripts.
        if len(manuscript_objs) == 0:
            return abort(404)
        # Using update_model_obj() to fetch the Manuscript object and update it
        # against request.json.
        manuscript_obj = update_model_obj(manuscript_id, Manuscript,
                                          create_or_update_argd_gen(Manuscript).generate_argd(request.json))
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
    """
    Implements a PATCH /authors/<id>/<id>/manuscripts/<id> endpoint. The row
    in the manuscripts table with that manuscript_id associated with those
    two author_ids in the authors_manuscripts table is updated from the JSON
    parameters.

    :author1_id:    One of the two author_ids associated with that
                    manuscript_id in the authors_manuscripts table.
    :author2_id:    The other of the two author_ids associated with that
                    manuscript_id in the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author1_obj.manuscripts))
        a2_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author2_obj.manuscripts))
        # Verifying that the two author_ids are associated with the
        # manuscript_id in authors_manuscripts.
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)
        # Using update_model_obj() to fetch the Manuscript object and update it
        # against request.json.
        manuscript_obj = update_model_obj(manuscript_id, Manuscript,
                                          create_or_update_argd_gen(Manuscript).generate_argd(request.json))
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>', methods=['DELETE'])
def delete_author_by_id(author_id: int):
    """
    Implements a DELETE /authors/<id> endpoint. The row in the authors
    table with that author_id is deleted. The row(s) in authors_books and
    authors_manuscripts tables with that author_id are also deleted.

    :author_id: The author_id of the row in the authors table to delete.
    :return:    A flask.Response object.
    """
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
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/books/<int:book_id>', methods=['DELETE'])
def delete_author_book(author_id: int, book_id: int):
    """
    Implements a DELETE /authors/<id>/books/<id> endpoint. The row in the
    books table with that book_id associated with that author_id in the
    authors_books table is deleted. The row(s) in authors_books table with
    that book_id are also deleted.

    :author_id: The author_id of the row in the authors table associated with
                this book_id.
    :book_id:   The book_id value of the row in the books table to
                delete.
    :return:    A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        # This step verifies that there is a row in authors_books with the given
        # author_id and the given book_id.
        if len(book_objs) == 0:
            return abort(404)
        book_obj, = book_objs
        # That row in authors_books must be deleted as well.
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/books/<int:book_id>', methods=['DELETE'])
def delete_authors_book(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a DELETE /authors/<id>/<id>/books/<id> endpoint. The row in
    the books table with that book_id associated with those author_ids in the
    authors_books table is deleted. The row(s) in authors_books table with that
    book_id are also deleted.

    :author1_id: The author_id of one of the two rows in the authors table
                 associated with this book_id.
    :author2_id: The author_id of the other of the two rows in the authors
                 table associated with this book_id.
    :book_id:    The book_id value of the row in the books table to
                 delete.
    :return:     A flask.Response object.
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author1_obj.books))
        a2_book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author2_obj.books))
        # This step verifies that the two author_ids each occur in a row in
        # authors_books with this book_id set.
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        book_obj, = a1_book_objs
        # That row in authors_books needs to be deleted too.
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_author_manuscript(author_id: int, manuscript_id: int):
    """
    Implements a DELETE /authors/<id>/manuscripts/<id> endpoint. The row in the
    manuscripts table with that manuscript_id associated with that author_id in
    the authors_manuscripts table is deleted. The row(s) in authors_manuscripts
    table with that manuscript_id are also deleted.

    :author_id:     The author_id of the row in the authors table associated
                    with this manuscript id.
    :manuscript_id: The manuscript_id value of the row in the manuscripts
                    table to delete.
    :return:        A flask.Response object.
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts))
        # This step verifies that there is a row in authors_manuscripts with the
        # given author_id and the given manuscript_id.
        if len(manuscript_objs) == 0:
            return abort(404)
        manuscript_obj, = manuscript_objs
        # That row in authors_manuscripts must be deleted as well.
        ab_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>', methods=['DELETE'])
def delete_authors_manuscript(author1_id: int, author2_id: int, manuscript_id: int):
    """
    Implements a DELETE /authors/<id>/<id>/manuscripts/<id> endpoint. The row in
    the manuscripts table with that id associated with those author_ids in the
    authors_books table is deleted. The row(s) in authors_manuscripts table with
    that manuscript id are also deleted.

    :author1_id:    The author_id of one of the two rows in the authors table
                    associated with this manuscript id.
    :author2_id:    The author_id of the other of the two rows in the authors
                    table associated with this manuscript id.
    :manuscript_id: The manuscript_id value of the row in the manuscripts
                    table to delete.
    :return:        A flask.Response object.
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        a1_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author1_obj.manuscripts))
        a2_manuscript_objs = list(filter(lambda bobj: bobj.manuscript_id == manuscript_id, author2_obj.manuscripts))
        # This step verifies that the two author_ids each occur in a row in
        # authors_manuscripts with this manuscript_id set.
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)

        manuscript_obj, = a1_manuscript_objs
        # That row in authors_manuscripts needs to be deleted too.
        ab_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return endpoint_action.handle_exception(exception)
