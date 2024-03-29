#!/usr/bin/python3

import itertools

from flask import Blueprint, Response, abort, jsonify, request

from risuspubl.api.utility import (
    crt_model_obj,
    crt_tbl_row_clos,
    check_json_req_props,
    disp_tbl_row_by_id_clos,
    disp_tbl_rows_clos,
    gen_crt_updt_argd,
    handle_exc,
    updt_model_obj,
    updt_tbl_row_by_id_clos,
)
from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    AuthorsBooks,
    AuthorsManuscripts,
    Book,
    Manuscript,
    db,
)


blueprint = Blueprint("authors", __name__, url_prefix="/authors")


# These functions return closures that implement endpoint functions,
# filling in the blank(s) with the provided class objects.


# A closure for GET /authors
disp_auths = disp_tbl_rows_clos(Author)

# A closure for POST /authors
crt_auth = crt_tbl_row_clos(Author)


# A closure for GET /authors/<id>
disp_auth_by_auid = disp_tbl_row_by_id_clos(Author)

# A closure for PATCH /authors/<id>
updt_auth_by_auid = updt_tbl_row_by_id_clos(Author)


@blueprint.route("/<int:author_id>/metadata", methods=["GET"])
def disp_auth_metdt_endpt(author_id: int):
    """
    Implements a GET /authors/{author_id}/metadata endpoint. The row
    in the authors_metadata table for that author_id is retrieved and
    displayed.

    :author_id: the value for the author_id column in the
    authors_metadata table
    :return: a flask.Response object
    """
    try:
        metadata_objs = list(
            AuthorMetadata.query.where(AuthorMetadata.author_id == author_id)
        )
        match len(metadata_objs):
            case 0:
                return abort(404)
            case 1:
                return jsonify(metadata_objs[0].serialize())
            case _:
                # Have more than one row for this author_id in the
                # author_metadata table fsr.
                return Response(
                    f"internal error: author_id {author_id} matches more than "
                    + "one row in authors_metadata table",
                    status=500,
                )
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["GET"])
def index_endpt():
    """
    Implements a GET /authors endpoint. All rows in the authors table
    are loaded and output as a JSON list.

    :return:    a flask.Response object
    """
    try:
        return disp_auths()
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author1_id>/<int:author2_id>/books", methods=["GET"])
def disp_auths_bks_endpt(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/{author1_id}/{author2_id}/books endpoint.
    All rows in the books table associated with those two author_ids in
    the authors_books table are loaded and output as a JSON list.

    :author1_id: One of the two author_ids associated with matching
    book_ids in the authors_books table.
    :author2_id: The other of the two author_ids associated with
    matching book_ids in the authors_books table.
    :return: a flask.Response object
    """
    try:
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id were identical")
        # A utility function is used to fetch a list of Book objects
        # whose book_id is associated with both author_ids in
        # authors_books.
        shared_books = _auths_shared_bkids(author1_id, author2_id)
        # The list is serialized and returned as json.
        retval = [book_obj.serialize() for book_obj in shared_books]
        return jsonify(retval)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/books/<int:book_id>", methods=["GET"]
)
def disp_auths_bk_by_bkid_endpt(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a GET /authors/{author1_id}/{author2_id}/books/{book_id}
    endpoint. The row in the books table with that book_id associated
    with those two author_ids in the authors_books table is loaded and
    outputed in JSON.

    :author1_id: One of the two author_ids associated with the given
    book_id in the authors_books table.
    :author2_id: The other of the two author_ids associated with the
    given book_id in the authors_books table.
    :book_id: The book_id of the row in the books table to load and
    display.
    :return: a flask.Response object
    """
    try:
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id were identical")
        # A utility function is used to fetch a list of Book objects
        # whose book_id is associated with both author_ids in
        # authors_books.
        shared_books = _auths_shared_bkids(author1_id, author2_id)
        # The Book object list is iterated over, looking for the object
        # with the matching book_id. If it's found, it's serialized and
        # returned as json.
        for book_obj in shared_books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        # If the book_id wasn't found, that's a 404.
        return abort(404)
    except Exception as exception:
        return handle_exc(exception)


# This private utility function is used by display_authors_manuscripts()
# and display_authors_manuscript_by_id() to generate a list of Book
# objects with manuscript_ids that are associated with both author_ids
# in the authors_manuscripts table.
def _auths_shared_msids(author1_id: int, author2_id: int) -> list:
    if author1_id == author2_id:
        raise ValueError("author1_id and author2_id were identical")
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    # The manuscripts attribute on an Author object comprises the
    # Manuscript objects whose manuscript_ids are associated with its
    # author_id in the authors_manuscripts table.
    author1_manuscripts = author1_obj.manuscripts
    author2_manuscripts = author2_obj.manuscripts
    # A dict of Manuscript objects by manuscript_id is built from both
    # lists chained in sequence.
    manuscript_objs_by_id = {
        manuscript_obj.manuscript_id: manuscript_obj
        for manuscript_obj in itertools.chain(author1_manuscripts, author2_manuscripts)
    }
    # Sets of manuscript_ids associated with each author_id are built
    # and intersected to find the shared manuscripts.
    shared_manuscript_ids = set(
        author1_manuscript_obj.manuscript_id
        for author1_manuscript_obj in author1_manuscripts
    ) & set(
        author2_manuscript_obj.manuscript_id
        for author2_manuscript_obj in author2_manuscripts
    )
    # The manuscript_ids are looked up in the dict via a list
    # comprehension and that list is returned.
    return [
        manuscript_objs_by_id[manuscript_id] for manuscript_id in shared_manuscript_ids
    ]


@blueprint.route("/<int:author1_id>/<int:author2_id>/manuscripts", methods=["GET"])
def disp_auths_mscrpts_endpt(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/{author1_id}/{author2_id}/manuscripts
    endpoint. All rows in the manuscripts table associated with those
    two author_ids in the authors_manuscripts table are loaded and
    output as a JSON list.

    :author1_id: One of the two author_ids associated with matching
    manuscript_ids in the authors_manuscripts table.
    :author2_id: The other of the two author_ids associated with
    matching manuscript_ids in the authors_manuscripts table.
    :return: a flask.Response object
    """
    try:
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id were identical")
        # This utility function looks up which manuscript_ids are
        # associated with both author_ids in authors_manuscripts and
        # returns Manuscript() objects for those manuscript_ids.
        shared_manuscripts = _auths_shared_msids(author1_id, author2_id)
        # A list of serializations is built # and returned via jsonify.
        retval = [manuscript_obj.serialize() for manuscript_obj in shared_manuscripts]
        return jsonify(retval)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>",
    methods=["GET"],
)
def disp_auths_mscrpt_by_msid_endpt(
    author1_id: int, author2_id: int, manuscript_id: int
):
    """
    Implements a GET
    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    associated with those two author_ids in the authors_manuscripts
    table is loaded and outputed in JSON.

    :author1_id: One of the two author_ids associated with the given
    manuscript_id in the authors_manuscripts table.
    :author2_id: The other of the two author_ids associated with the
    given manuscript_id in the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to load and display.
    :return: a flask.Response object
    """
    try:
        # Using a utility function to look up which manuscript_ids are
        # associated with both author_ids in authors_manuscripts and
        # return Manuscript() objects for those manuscript_ids.
        shared_manuscripts = _auths_shared_msids(author1_id, author2_id)
        # Iterating across the Manuscript object list until the object
        # with the matching manuscript_id is found.
        for manuscript_obj in shared_manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        # If the loop completed and the Manuscript() object wasn't
        # found, that's a 404.
        return abort(404)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>", methods=["GET"])
def disp_auth_by_auid_endpt(author_id: int):
    """
    Implements a GET /authors/{author_id} endpoint. The row in the
    authors table with the given author_id is loaded and output in JSON.

    :author_id: The author_id of the row in the authors table to load
    and display.
    :return: a flask.Response object
    """
    try:
        return disp_auth_by_auid(author_id)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/books", methods=["GET"])
def disp_auth_bks_endpt(author_id: int):
    """
    Implements a GET /authors/{author_id}/books endpoint. All rows in
    the books table associated with that author_id in the authors_books
    table are loaded and output as a JSON list.

    :author_id: The author_id associated with book_ids in the
    authors_books table of rows from the books table to display.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [book_obj.serialize() for book_obj in author_obj.books]
        return jsonify(retval)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/books/<int:book_id>", methods=["GET"])
def disp_auth_bk_by_bkid_endpt(author_id: int, book_id: int):
    """
    Implements a GET /authors/{author_id}/books/{book_id} endpoint.
    The row in the books table with that book_id associated with that
    author_id in the authors_books table is loaded and outputed in JSON.

    :author_id: The author_id associated with the given book_id in the
    authors_books table.
    :book_id: The book_id of the row in the books table to load and
    display.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        # Iterating across the Author.manuscripts list looking for a
        # Book object by that id. If it's found, it's serialized and
        # returned as JSON. Otherwise, a 404 error is raised.
        for book_obj in author_obj.books:
            if book_obj.book_id != book_id:
                continue
            return jsonify(book_obj.serialize())
        return Response(
            f"author with author_id {author_id} does not have a book with "
            + f"book_id {book_id}",
            status=400,
        )
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/manuscripts", methods=["GET"])
def disp_auth_mscrpts_endpt(author_id: int):
    """
    Implements a GET /authors/{author_id}/manuscripts endpoint. All rows
    in the manuscripts table associated with that author_ids in the
    authors_manuscripts table are loaded and output as a JSON list.

    :author_id: The author_id associated with manuscript_ids in the
    authors_manuscripts table of rows from the manuscripts table to
    display.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        retval = [
            manuscript_obj.serialize() for manuscript_obj in author_obj.manuscripts
        ]
        return jsonify(retval)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/manuscripts/<int:manuscript_id>", methods=["GET"])
def disp_auth_mscrpt_by_msid_endpt(author_id: int, manuscript_id: int):
    """
    Implements a GET /authors/{author_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    associated with that author_id in the authors_manuscripts table is
    loaded and outputed in JSON.

    :author_id: The author_id associated with the given manuscript_id in
    the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to load and display.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        # Iterating across the Author.manuscripts list looking for a
        # Manuscript object by that id. If it's found, it's serialized
        # and returned as JSON. Otherwise, a 404 error is raised.
        for manuscript_obj in author_obj.manuscripts:
            if manuscript_obj.manuscript_id != manuscript_id:
                continue
            return jsonify(manuscript_obj.serialize())
        return abort(404)
    except Exception as exception:
        return handle_exc(exception)


# To be frank this endpoint doesn't have much of a reason
# to exist, save that if this endpoint is loaded something
# *should* be here since /authors/{author_id} is valid and
# /authors/{author1_id}/{author2_id}/books is valid. Provied for
# completeness.
@blueprint.route("/<int:author1_id>/<int:author2_id>", methods=["GET"])
def disp_auths_by_auids_endpt(author1_id: int, author2_id: int):
    """
    Implements a GET /authors/{author_id}/{author_id} endpoint. The
    rows in the authors table with those two author_ids are loaded and
    outputed in a JSON list.

    :author1_id: One of the two author_ids of rows in the authors table
    to load and display.
    :author2_id: The other of the two author_ids of rows in the authors
    table to load and display.
    :return: a flask.Response object
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        # The two author_objs are serialized and returned as a 2-element
        # json list.
        retval = [author1_obj.serialize(), author2_obj.serialize()]
        return jsonify(retval)
    except Exception as exception:
        return handle_exc(exception)


# This private utility function is used by display_authors_books() and
# display_authors_book_by_id() to generate a list of Book objects with
# book_ids that are associated with both author_ids in the authors_books
# table.
def _auths_shared_bkids(author1_id: int, author2_id: int) -> list:
    author1_obj = Author.query.get_or_404(author1_id)
    author2_obj = Author.query.get_or_404(author2_id)
    # The books attribute on an Author object comprises the Book
    # objects whose book_ids are associated with its author_id in the
    # authors_books table.
    author1_books = author1_obj.books
    author2_books = author2_obj.books
    # A dict of Book objects by book_id is built from both lists chained
    # in sequence.
    book_objs_by_id = {
        book_obj.book_id: book_obj
        for book_obj in itertools.chain(author1_books, author2_books)
    }
    # Sets of book_ids associated with each author_id are built and
    # intersected to find the shared books.
    shared_book_ids = set(
        author1_book_obj.book_id for author1_book_obj in author1_books
    ) & set(author2_book_obj.book_id for author2_book_obj in author2_books)
    # The book_ids are looked up in the dict via a list comprehension
    # and that list is returned.
    return [book_objs_by_id[book_id] for book_id in shared_book_ids]


@blueprint.route("/<int:author_id>/metadata", methods=["PATCH"])
def updt_auth_metdt_endpt(author_id: int):
    """
    Implements a PATCH /authors/{author_id}/metadata endpoint. The row
    in the authors_metadata table associated with the given author_id is
    updated from the JSON parameters.

    :author_id: the author_id to locate the row to change in the
    authors_metadata table with
    :return: a flask.Response object
    """
    try:
        check_json_req_props(
            AuthorMetadata, request.json, {"author_metadata_id"}, chk_missing=False
        )
        author_metadata_objs = (
            db.session.query(AuthorMetadata).filter_by(author_id=author_id).all()
        )
        match len(author_metadata_objs):
            case 0:
                return abort(404)
            case 1:
                author_metadata_id = author_metadata_objs[0].author_metadata_id
                # We have the model subclass object, but the endpoint
                # closure takes the author_metadata_id and grabs the
                # object itself. A little wasteful, nbd. Updates the
                # object and returns it, it's saved, serialized,
                # jsonified and returned.
                author_metadata_obj = updt_model_obj(
                    author_metadata_id,
                    AuthorMetadata,
                    gen_crt_updt_argd(AuthorMetadata, request.json),
                )
                db.session.add(author_metadata_obj)
                db.session.commit()
                return jsonify(author_metadata_obj.serialize())
            case _:
                # Have more than one row for this author_id in the
                # author_metadata table fsr.
                return Response(
                    f"internal error: author_id {author_id} matches more than "
                    + "one row in authors_metadata table",
                    status=500,
                )
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/books/<int:book_id>", methods=["PATCH", "PUT"]
)
def updt_auths_bk_endpt(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a PATCH
    /authors/{author1_id}/{author2_id}/books/{book_id} endpoint. The
    row in the books table with that book_id associated with those two
    author_ids in the authors_books table is updated from the JSON
    parameters.

    :author1_id: One of the two author_ids associated with that book_id
    in the authors_books table.
    :author2_id: The other of the two author_ids associated with that
    book_id in the authors_books table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        # Check the request JSON for the correct set of properties.
        check_json_req_props(
            Book, request.json, {"book_id"}, {"series_id"}, chk_missing=False
        )
        # Check that both the Author objects exist.
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        # Grabbing each Author object's associated Book objects, looking
        # for one with an id matching the book_id arg. If either list is
        # empty, errors out with a 404.
        a1_book_objs = list(
            filter(lambda bobj: bobj.book_id == book_id, author1_obj.books)
        )
        a2_book_objs = list(
            filter(lambda bobj: bobj.book_id == book_id, author2_obj.books)
        )
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        # The book_id checks out, so the update closure is used to
        # update it. The Book object is saved, serialized and jsonified.
        book_obj = updt_model_obj(book_id, Book, gen_crt_updt_argd(Book, request.json))
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>",
    methods=["PATCH", "PUT"],
)
def updt_auths_mscrpt_endpt(author1_id: int, author2_id: int, manuscript_id: int):
    """
    Implements a PATCH
    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    associated with those two author_ids in the authors_manuscripts
    table is updated from the JSON parameters.

    :author1_id: One of the two author_ids associated with that
    manuscript_id in the authors_manuscripts table.
    :author2_id: The other of the two author_ids associated with that
    manuscript_id in the authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to update.
    :return: a flask.Response object
    """
    try:
        # Check the request JSON for the correct set of properties.
        check_json_req_props(
            Manuscript,
            request.json,
            {"manuscript_id"},
            {"series_id"},
            chk_missing=False,
        )
        # Check that both the Author objects exist.
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        # Grabbing each Author object's associated Manuscript objects,
        # looking for one with an id matching the manuscript_id arg. If
        # either list is empty, errors out with a 404.
        a1_manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id,
                author1_obj.manuscripts,
            )
        )
        a2_manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id,
                author2_obj.manuscripts,
            )
        )
        # Verifying that the two author_ids are associated with the
        # manuscript_id in authors_manuscripts.
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)
        # Using updt_model_obj() to fetch the Manuscript object and
        # update it against request.json.
        manuscript_obj = updt_model_obj(
            manuscript_id,
            Manuscript,
            gen_crt_updt_argd(Manuscript, request.json),
        )
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>", methods=["PATCH", "PUT"])
def updt_auth_by_auid_endpt(author_id: int):
    """
    Implements a PATCH /authors/{author_id} endpoint. The row in
    the authors table with that author_id is updated from the JSON
    parameters.

    :author_id: The author_id of the row in the authors table to update.
    :return: a flask.Response object
    """
    try:
        return updt_auth_by_auid(author_id, request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/books/<int:book_id>", methods=["PATCH", "PUT"])
# HERE
def updt_auth_bk_endpt(author_id: int, book_id: int):
    """
    Implements a PATCH /authors/{author_id}/books/{book_id} endpoint.
    The row in the books table with that book_id associated with that
    author_id in the authors_books table is updated from the JSON
    parameters.

    :author_id: The author_id associated with that book_id in the
    authors_books table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        check_json_req_props(
            Book, request.json, {"book_id"}, {"series_id"}, chk_missing=False
        )
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        # Verifying that this author_id is associated with this book_id
        # in authors_books.
        if len(book_objs) == 0:
            return abort(404)
        # Using updt_model_obj() to fetch the Book object and update it
        # against request.json.
        book_obj = updt_model_obj(book_id, Book, gen_crt_updt_argd(Book, request.json))
        db.session.add(book_obj)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author_id>/manuscripts/<int:manuscript_id>", methods=["PATCH", "PUT"]
)
def updt_auth_mscrpt_endpt(author_id: int, manuscript_id: int):
    """
    Implements a PATCH /authors/{author_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    associated with that author_id in the authors_manuscripts table is
    updated from the JSON parameters.

    :author_id: The author_id associated with that manuscript_id in the
    authors_manuscripts table.
    :manuscript_id: The manuscript_id of the row in the manuscripts
    table to update.
    :return: a flask.Response object
    """
    try:
        check_json_req_props(
            Manuscript, request.json, {"manuscript_id"}, chk_missing=False
        )
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts
            )
        )
        # Verifying that this author_id is associated with this
        # manuscript_id in authors_manuscripts.
        if len(manuscript_objs) == 0:
            return abort(404)
        # Using updt_model_obj() to fetch the Manuscript object and
        # update it against request.json.
        manuscript_obj = updt_model_obj(
            manuscript_id,
            Manuscript,
            gen_crt_updt_argd(Manuscript, request.json),
        )
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/metadata", methods=["POST"])
def crt_auth_metdt_endpt(author_id: int):
    """
    Implements a POST /authors/{author_id}/metadata endpoint. Creates
    a row in the authors_metadata table with the given author_id
    from the JSON parameters. Fails if there already is a row in the
    authors_metadata table with that author_id value.

    :author_id: the author_id value to set on the new row in the
    authors_metadata table
    :return: a flask.Response object
    """
    try:
        check_json_req_props(
            AuthorMetadata, request.json, {"author_metadata_id", "author_id"}
        )
        Author.query.get_or_404(author_id)
        check_json_req_props(
            AuthorMetadata, request.json, {"author_id", "author_metadata_id"}
        )
        results = tuple(
            AuthorMetadata.query.where(AuthorMetadata.author_id == author_id)
        )
        if len(results):
            raise ValueError(
                f"metadata for author with id {author_id} already exists; cannot create anew"
            )

        query_dict = dict(author_id=author_id, **request.json)
        author_metadata_obj = crt_model_obj(
            AuthorMetadata, gen_crt_updt_argd(AuthorMetadata, query_dict)
        )
        db.session.add(author_metadata_obj)
        db.session.commit()
        return jsonify(author_metadata_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("", methods=["POST"])
def auth_crt_endpt():
    """
    Implements a POST /authors endpoint. A new row in the authors table
    is constituted from the JSON parameters and saved to that table.

    :return: a flask.Response object
    """
    try:
        check_json_req_props(Author, request.json, {"author_id"})
        return crt_auth(request.json)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author1_id>/<int:author2_id>/books", methods=["POST"])
def crt_auths_bk_endpt(author1_id: int, author2_id: int):
    """
    Implements a POST /authors/{author_id}/books endpoint. A new row in
    the books table is constituted from the JSON parameters and saved to
    that table. In addition, rows in the authors_books table associating
    the new book_id with those two author_ids are added.

    :author1_id: One of the two author_ids to associate the new book_id
    with in the authors_books table.
    :author2_id: The other of the two author_ids to associate the new
    book_id with in the authors_books table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        check_json_req_props(Book, request.json, {"book_id"}, {"series_id"})
        # Using crt_model_obj() to process request.json into a Book()
        # argument dict and instance a Book() object.
        book_obj = crt_model_obj(
            Book,
            gen_crt_updt_argd(Book, request.json),
            optional_params={"series_id"},
        )
        db.session.add(book_obj)
        db.session.commit()
        # Associating the new book_id with both author_ids in the
        # authors_books table.
        ab1_insert = AuthorsBooks.insert().values(
            author_id=author1_id, book_id=book_obj.book_id
        )
        ab2_insert = AuthorsBooks.insert().values(
            author_id=author2_id, book_id=book_obj.book_id
        )
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author1_id>/<int:author2_id>/manuscripts", methods=["POST"])
def crt_auths_mscrpt_endpt(author1_id: int, author2_id: int):
    """
    Implements a POST /authors/{author1_id}/{author2_id}/manuscripts
    endpoint. A new row in the manuscripts table is constituted from the
    JSON parameters and saved to that table. In addition, rows in the
    authors_manuscripts table associating the new manuscript_id with
    those two author_ids are added.

    :author1_id: One of the two author_ids to associate the new
    manuscript_id with in the authors_manuscripts table.
    :author2_id: The other of the two author_ids to associate the new
    manuscript_id with in the authors_manuscripts table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        Author.query.get_or_404(author1_id)
        Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        check_json_req_props(Manuscript, request.json, {"manuscript_id"}, {"series_id"})
        # Using crt_model_obj() to process request.json into a
        # Manuscript() argument dict and instance a Manuscript() object.
        manuscript_obj = crt_model_obj(
            Manuscript,
            gen_crt_updt_argd(Manuscript, request.json),
            optional_params={"series_id"},
        )
        db.session.add(manuscript_obj)
        db.session.commit()
        # Associating the new manuscript_id with both author_ids in the
        # authors_manuscripts table.
        ab1_insert = AuthorsManuscripts.insert().values(
            author_id=author1_id, manuscript_id=manuscript_obj.manuscript_id
        )
        ab2_insert = AuthorsManuscripts.insert().values(
            author_id=author2_id, manuscript_id=manuscript_obj.manuscript_id
        )
        db.session.execute(ab1_insert)
        db.session.execute(ab2_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/books", methods=["POST"])
def crt_auth_bk_endpt(author_id: int):
    """
    Implements a POST /authors/{author_id}/books endpoint. A new row
    in the books table is constituted from the JSON parameters and
    saved to that table. In addition, a row in the authors_books table
    associating the new book_id with that author_id is added.

    :author_id: The author_id to associate the new book_id with in the
    authors_books table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        Author.query.get_or_404(author_id)
        # Using crt_model_obj() to process request.json into a Book()
        # argument dict and instance a Book() object.
        check_json_req_props(
            Book, request.json, {"author_id", "book_id"}, {"series_id"}
        )
        book_obj = crt_model_obj(
            Book,
            gen_crt_updt_argd(Book, request.json),
            optional_params={"series_id"},
        )
        db.session.add(book_obj)
        db.session.commit()
        # Associating the new book_id with both author_ids in the
        # authors_books table.
        ab_insert = AuthorsBooks.insert().values(
            author_id=author_id, book_id=book_obj.book_id
        )
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(book_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/manuscripts", methods=["POST"])
def crt_auth_mscrpt_endpt(author_id: int):
    """
    Implements a POST /authors/{author_id}/manuscripts endpoint. A
    new row in the manuscripts table is constituted from the JSON
    parameters and saved to that table. In addition, a row in the
    authors_manuscripts table associating the new manuscript_id with
    that author_id is added.

    :author_id: The author_id to associate the new manuscript_id with in
    the authors_manuscripts table.
    :book_id: The book_id of the row in the books table to update.
    :return: a flask.Response object
    """
    try:
        check_json_req_props(Manuscript, request.json, {"manuscript_id"})
        Author.query.get_or_404(author_id)
        # Using crt_model_obj() to process request.json into a
        # Manuscript() argument dict and instance a Manuscript() object.
        manuscript_obj = crt_model_obj(
            Manuscript,
            gen_crt_updt_argd(Manuscript, request.json),
            optional_params={"series_id"},
        )
        db.session.add(manuscript_obj)
        db.session.commit()
        # Associating the new manuscript_id with the author_id in the
        # authors_manuscripts table.
        ab_insert = AuthorsManuscripts.insert().values(
            author_id=author_id, manuscript_id=manuscript_obj.manuscript_id
        )
        db.session.execute(ab_insert)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/metadata", methods=["DELETE"])
def del_auth_metdt_endpt(author_id: int):
    """
    Implements a DELETE /authors/{author_id}/metadata endpoint. Locates
    the row in the authors_metadata table with the specified author_id
    value and deletes it.

    :author_id: the value for the author_id column to use when locating
    the row in the authors_metadata table to delete
    :return: a flask.Response object
    """
    try:
        metadata_objs = tuple(
            AuthorMetadata.query.where(AuthorMetadata.author_id == author_id)
        )
        if len(metadata_objs) == 0:
            return abort(404)
        elif len(metadata_objs) > 1:
            return Response(
                f"internal error: author_id {author_id} matches more than one row in "
                "authors_metadata table",
                status=500,
            )
        (metadata_obj,) = metadata_objs
        db.session.delete(metadata_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/books/<int:book_id>", methods=["DELETE"]
)
def del_auths_bk_endpt(author1_id: int, author2_id: int, book_id: int):
    """
    Implements a DELETE
    /authors/{author1_id}/{author2_id}/books/{book_id} endpoint. The
    row in the books table with that book_id associated with those
    author_ids in the authors_books table is deleted. The row(s) in
    authors_books table with that book_id are also deleted.

    :author1_id: The author_id of one of the two rows in the authors
    table associated with this book_id.
    :author2_id: The author_id of the other of the two rows in the
    authors table associated with this book_id.
    :book_id: The book_id value of the row in the books table to delete.
    :return: a flask.Response object
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        a1_book_objs = list(
            filter(lambda bobj: bobj.book_id == book_id, author1_obj.books)
        )
        a2_book_objs = list(
            filter(lambda bobj: bobj.book_id == book_id, author2_obj.books)
        )
        # This step verifies that the two author_ids each occur in a row
        # in authors_books with this book_id set.
        if len(a1_book_objs) == 0 or len(a2_book_objs) == 0:
            return abort(404)
        (book_obj,) = a1_book_objs
        # That row in authors_books needs to be deleted too.
        ab_del = AuthorsBooks.delete().where(AuthorsBooks.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route(
    "/<int:author1_id>/<int:author2_id>/manuscripts/<int:manuscript_id>",
    methods=["DELETE"],
)
def del_auths_mscrpt_endpt(author1_id: int, author2_id: int, manuscript_id: int):
    """
    Implements a DELETE
    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that id associated
    with those author_ids in the authors_books table is deleted. The
    row(s) in authors_manuscripts table with that manuscript id are also
    deleted.

    :author1_id: The author_id of one of the two rows in the authors
    table associated with this manuscript id.
    :author2_id: The author_id of the other of the two rows in the
    authors table associated with this manuscript id.
    :manuscript_id: The manuscript_id value of the row in the
    manuscripts table to delete.
    :return: a flask.Response object
    """
    try:
        author1_obj = Author.query.get_or_404(author1_id)
        author2_obj = Author.query.get_or_404(author2_id)
        if author1_id == author2_id:
            raise ValueError("author1_id and author2_id are equal")
        a1_manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id,
                author1_obj.manuscripts,
            )
        )
        a2_manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id,
                author2_obj.manuscripts,
            )
        )
        # This step verifies that the two author_ids each occur in a row
        # in authors_manuscripts with this manuscript_id set.
        if len(a1_manuscript_objs) == 0 or len(a2_manuscript_objs) == 0:
            return abort(404)

        (manuscript_obj,) = a1_manuscript_objs
        # That row in authors_manuscripts needs to be deleted too.
        ab_del = AuthorsManuscripts.delete().where(
            AuthorsManuscripts.columns[1] == manuscript_id
        )
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>", methods=["DELETE"])
def del_auth_by_auid_endpt(author_id: int):
    """
    Implements a DELETE /authors/{author_id} endpoint. The row in
    the authors table with that author_id is deleted. The row(s) in
    authors_books and authors_manuscripts tables with that author_id are
    also deleted.

    :author_id: The author_id of the row in the authors table to delete.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        ab_del = AuthorsBooks.delete().where(AuthorsBooks.columns[0] == author_id)
        db.session.execute(ab_del)
        am_del = AuthorsManuscripts.delete().where(
            AuthorsManuscripts.columns[0] == author_id
        )
        db.session.execute(am_del)
        db.session.commit()
        db.session.delete(author_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/books/<int:book_id>", methods=["DELETE"])
def del_auth_bk_endpt(author_id: int, book_id: int):
    """
    Implements a DELETE /authors/{author_id}/books/{book_id} endpoint.
    The row in the books table with that book_id associated with that
    author_id in the authors_books table is deleted. The row(s) in
    authors_books table with that book_id are also deleted.

    :author_id: The author_id of the row in the authors table associated
    with this book_id.
    :book_id: The book_id value of the row in the books table to delete.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        book_objs = list(filter(lambda bobj: bobj.book_id == book_id, author_obj.books))
        # This step verifies that there is a row in authors_books with
        # the given author_id and the given book_id.
        if len(book_objs) == 0:
            return abort(404)
        (book_obj,) = book_objs
        # That row in authors_books must be deleted as well.
        ab_del = AuthorsBooks.delete().where(AuthorsBooks.columns[1] == book_id)
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(book_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)


@blueprint.route("/<int:author_id>/manuscripts/<int:manuscript_id>", methods=["DELETE"])
def del_auth_mscrpt_endpt(author_id: int, manuscript_id: int):
    """
    Implements a DELETE /authors/{author_id}/manuscripts/{manuscript_id}
    endpoint. The row in the manuscripts table with that manuscript_id
    associated with that author_id in the authors_manuscripts table
    is deleted. The row(s) in authors_manuscripts table with that
    manuscript_id are also deleted.

    :author_id: The author_id of the row in the authors table associated
    with this manuscript id.
    :manuscript_id: The manuscript_id value of the row in the
    manuscripts table to delete.
    :return: a flask.Response object
    """
    try:
        author_obj = Author.query.get_or_404(author_id)
        manuscript_objs = list(
            filter(
                lambda bobj: bobj.manuscript_id == manuscript_id, author_obj.manuscripts
            )
        )
        # This step verifies that there is a row in authors_manuscripts
        # with the given author_id and the given manuscript_id.
        if len(manuscript_objs) == 0:
            return abort(404)
        (manuscript_obj,) = manuscript_objs
        # That row in authors_manuscripts must be deleted as well.
        ab_del = AuthorsManuscripts.delete().where(
            AuthorsManuscripts.columns[1] == manuscript_id
        )
        db.session.execute(ab_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        return handle_exc(exception)
