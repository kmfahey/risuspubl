#!/usr/bin/python3

from flask import Blueprint, jsonify
from risuspubl.api.utility import handle_exc


blueprint = Blueprint("docroot", __name__, url_prefix="/")

HELP_JSOBJ = {
    "docroot": {
        "/": {"GET": "Returns this help object."},
    },
    "authors": {
        "/authors": {
            "POST": "Adds the submitted object as a new author.",
            "GET": "Returns a list of all authors.",
        },
        "/authors/{{authorId}}": {
            "DELETE": "Deletes the author with author id {{authorId}}.",
            "GET": "Displays the author with author id {{authorId}}.",
            "PATCH": (
                "Updates the author with author id {{authorId}} according to "
                + "the data submitted.",
            ),
        },
        "/authors/{{authorId}}/books": {
            "GET": (
                "Displays a list of all books by the author with author id "
                + "{{authorId}}."
            ),
            "POST": (
                "Adds the submitted object as a new book and associates it "
                + "with the author identified by {{authorId}}."
            ),
        },
        "/authors/{{authorId}}/books/{{bookId}}": {
            "DELETE": (
                "Disassociates the book with book id {{bookId}} from the "
                + "author with author id {{authorId}}, and deletes the book."
            ),
            "GET": (
                "Displays the book with book id {{bookId}} by the author with "
                + "author id {{authorId}}."
            ),
            "PATCH": (
                "Updates the book with book id {{bookId}}, that is by the "
                + "author with author id {{authorId}}, according to the data submitted."
            ),
        },
        "/authors/{{authorId}}/manuscripts": {
            "GET": (
                "Displays a list of all manuscripts by the author with author "
                + "id {{authorId}}."
            ),
            "POST": (
                "Adds the submitted object as a new manuscript and associates "
                + "it with the author identified by {{authorId}}."
            ),
        },
        "/authors/{{authorId}}/manuscripts/{{manuscriptId}}": {
            "DELETE": (
                "Disassociates the manuscript with manuscript id "
                + "{{manuscriptId}} from the author with author id "
                + "{{authorId}}, and deletes the manuscript."
            ),
            "GET": (
                "Displays the manuscript with manuscript id {{manuscriptId}} "
                + "by the author with author id {{authorId}}."
            ),
            "PATCH": (
                "Updates the book with book id {{bookId}}, that is by the "
                + "author with author id {{authorId}}, according to the data "
                + "submitted."
            ),
        },
        "/authors/{{authorId}}/metadata": {
            "DELETE": (
                "Deletes the metadata for the author with author id {{authorId}}."
            ),
            "GET": (
                "Displays the metadata for the author with author id {{authorId}}."
            ),
            "PATCH": (
                "Updates the metadata of the author with author id "
                + "{{authorId}} according to the data submitted."
            ),
            "POST": (
                "Adds the submitted object as metadata associated with "
                + "{{authorId}}."
            ),
        },
        "/authors/{{authorOneId}}/{{authorTwoId}}": {
            "GET": (
                "Displays the authors with author ids {{authorOneId}} and "
                + "{{authorTwoId}}."
            ),
        },
        "/authors/{{authorOneId}}/{{authorTwoId}}/books": {
            "GET": (
                "Displays a list of all books that are a collaboration "
                + "between the authors with author ids {{authorOneId}} and "
                + "{{authorTwoId}}."
            ),
            "POST": (
                "Adds the submitted object as a new book and associates it "
                + "with {{authorOneId}} and {{authorTwoId}}."
            ),
        },
        "/authors/{{authorOneId}}/{{authorTwoId}}/books/{{bookId}}": {
            "DELETE": (
                "Disassociates the book with book id {{bookId}} from the "
                + "authors with author ids {{authorOneId}} and "
                + "{{authorTwoId}}, and deletes the book."
            ),
            "GET": (
                "Displays the book with book id {{bookId}} that is by the "
                + "authors with author ids {{authorOneId}} and {{authorTwoId}}."
            ),
            "PATCH": (
                "Updates the book with book id {{bookId}}, that is by the "
                + "authors with author ids {{authorOneId}} and "
                + "{{authorOneId}}, according to the data submitted."
            ),
        },
        "/authors/{{authorOneId}}/{{authorTwoId}}/manuscripts": {
            "GET": (
                "Displays a list of all manuscripts that are a collaboration "
                + "between the authors with author ids {{authorOneId}} and "
                + "{{authorTwoId}}."
            ),
            "POST": (
                "Adds the submitted object as a new manuscript and associates "
                + "it with {{authorOneId}} and {{authorTwoId}}."
            ),
        },
        "/authors/{{authorOneId}}/{{authorTwoId}}/manuscripts/{{manuscriptId}}": {
            "DELETE": (
                "Disassociates the manuscript with manuscript id "
                + "{{manuscriptId}} from the authors with author ids "
                + "{{authorOneId}} and {{authorTwoId}}, and deletes the "
                + "manuscript."
            ),
            "GET": (
                "Displays the manuscript with manuscript id {{manuscriptId}} "
                + "that is by the authors with author ids {{authorOneId}} and "
                + "{{authorTwoId}}."
            ),
            "PATCH": (
                "Updates the manuscript with manuscript id {{manuscriptId}}, "
                + "that is by the authors with author ids {{authorOneId}} and "
                + "{{authorOneId}}, according to the data submitted."
            ),
        },
    },
    "books": {
        "/books": {"GET": "Displays a list of all books."},
        "/books/{{bookId}}": {
            "DELETE": "Deletes the book with book id {{bookId}}.",
            "GET": "Displays the book with book id {{bookId}}.",
            "PATCH": (
                "Updates the book with book id {{bookId}} according to the "
                + "data submitted."
            ),
        },
    },
    "clients": {
        "/clients": {
            "GET": "Displays a list of all clients.",
            "POST": "Adds the submitted object as a new client.",
        },
        "/clients/{{clientId}}": {
            "DELETE": "Deletes the client with client id {{clientId}}.",
            "GET": "Displays the client with client id {{clientId}}.",
            "PATCH": (
                "Updates the client with client id {{clientId}} according to "
                + "the data submitted."
            ),
        },
    },
    "editors": {
        "/editors": {
            "GET": "Displays a list of all editors.",
            "POST": "Adds the submitted object as a new editor.",
        },
        "/editors/{{editorId}}": {
            "DELETE": "Deletes the editor with editor id {{editorId}}.",
            "GET": "Displays the editor with editor id {{editorId}}.",
            "PATCH": (
                "Updates the editor with editor id {{editorId}} according to "
                + "the data submitted."
            ),
        },
        "/editors/{{editorId}}/books": {
            "GET": (
                "Displays a list of all books that the editor with editor id "
                + "{{editorId}} was the editor on."
            ),
        },
        "/editors/{{editorId}}/books/{{bookId}}": {
            "DELETE": (
                "Disassociates the book with book id {{bookId}} from the "
                + "editor with editor id {{editorId}}, and deletes the book."
            ),
            "GET": (
                "Displays the book with book id {{bookId}} that the editor "
                + "with editor id {{editorId}} was the editor on."
            ),
            "PATCH": (
                "Updates the book with book id {{bookId}}, that was edited by "
                + "the editor with editor id {{editorId}},  according to the "
                + "data submitted."
            ),
        },
        "/editors/{{editorId}}/manuscripts": {
            "GET": (
                "Displays a list of all manuscripts that the editor with "
                + "editor id {{editorId}} was the editor on."
            )
        },
        "/editors/{{editorId}}/manuscripts/{{manuscriptId}}": {
            "DELETE": (
                "Disassociates the manuscript with manuscript id "
                + "{{manuscriptId}} from the editor with editor id "
                + "{{editorId}}, and deletes the manuscript."
            ),
            "GET": (
                "Displays the manuscript with manuscript id {{manuscriptId}} "
                + "that the editor with editor id {{editorId}} was the editor "
                + "on."
            ),
            "PATCH": (
                "Updates the manuscript with manuscript id {{manuscriptId}}, "
                + "that was edited by the editor with editor id {{editorId}}, "
                + "according to the data submitted."
            ),
        },
    },
    "manuscripts": {
        "/manuscripts": {"GET": "Displays a list of all manuscripts."},
        "/manuscripts/{{manuscriptId}}": {
            "DELETE": "Deletes the manuscript with manuscript id {{manuscriptId}}.",
            "GET": "Displays the manuscript with manuscript id {{manuscriptId}}.",
            "PATCH": (
                "Updates the manuscript with manuscript id {{manuscriptId}} "
                + "according to the data submitted."
            ),
        },
    },
    "sales_records": {
        "/sales_records/books/{{bookId}}": {
            "GET": "Displays the sales records for the book with book id {{bookId}}."
        },
        "/sales_records/years/{{year}}": {
            "GET": (
                "Displays all sales records for the year {{year}}, in "
                + "chronological order."
            )
        },
        "/sales_records/years/{{year}}/books/{{bookId}}": {
            "GET": (
                "Displays all sales records for the book with book id "
                + "{{bookId}} for the year {{year}}, in chronological order."
            )
        },
        "/sales_records/years/{{year}}/months/{{month}}": {
            "GET": (
                "Displays all sales records for the month and year {{month}} "
                + "and {{year}}."
            )
        },
        "/sales_records/years/{{year}}/months/{{month}}/books/{{bookId}}": {
            "GET": (
                "Displays all sales records for the book with book id "
                + "{{bookId}} for the month and year {{month}} and {{year}}."
            )
        },
        "/sales_records/{{salesRecordId}}": {
            "GET": "Displays the sales record with sales record id {{salesRecordId}}."
        },
    },
    "salespeople": {
        "/salespeople": {
            "GET": "Displays a list of all salespeople.",
            "POST": "Adds the submitted object as a new salesperson.",
        },
        "/salespeople/{{salespersonId}}": {
            "DELETE": (
                "Deletes the salesperson with salesperson id {{salespersonId}}."
            ),
            "GET": (
                "Displays the salesperson with the salesperson id {{salespersonId}}."
            ),
            "PATCH": (
                "Updates the salesperson with salesperson id "
                + "{{salespersonId}} according to the data submitted."
            ),
        },
        "/salespeople/{{salespersonId}}/clients": {
            "GET": (
                "Displays a list of all clients that the salesperson with "
                + "salesperson id {{salespersonId}} handles."
            ),
            "POST": (
                "Adds the submitted object as a new client and associates it "
                + "with the salesperson identified by {{salespersonId}}."
            ),
        },
        "/salespeople/{{salespersonId}}/clients/{{clientId}}": {
            "DELETE": (
                "Disassociates the client with client id {{clientId}} from "
                + "the salesperson with salesperson id {{salespersonId}}, and "
                + "deletes the client."
            ),
            "GET": (
                "Displays the client with client id {{clientId}} that the "
                + "salesperson with salesperson id {{salespersonId}} handles."
            ),
            "PATCH": (
                "Updates the client with client id {{clientId}}, who is "
                + "handled by the salesperson with salesperson id "
                + "{{salespersonId}}, according to the data submitted."
            ),
        },
    },
    "series": {
        "/series": {
            "GET": "Displays a list of all book series.",
            "POST": "Adds the submitted object as a new series.",
        },
        "/series/{{seriesId}}": {
            "DELETE": "Deletes the series with series id {{seriesId}}.",
            "GET": "Displays the series with series id {{seriesId}}.",
            "PATCH": (
                "Updates the series with series id {{seriesId}} according to "
                + "the data submitted."
            ),
        },
        "/series/{{seriesId}}/books": {
            "GET": (
                "Displays a list of the books in the series with series id "
                + "{{seriesId}}."
            )
        },
        "/series/{{seriesId}}/books/{{bookId}}": {
            "GET": (
                "Displays the book with book id {{bookId}} that is in the "
                + "series with series id {{seriesId}}."
            ),
            "PATCH": (
                "Updates the book with book id {{bookId}}, that is part of "
                + "the series with series id {{seriesId}}, according to the "
                + "data submitted."
            ),
        },
        "/series/{{seriesId}}/manuscripts": {
            "GET": (
                "Displays a list of the manuscripts in the series with series "
                + "id {{seriesId}}."
            )
        },
        "/series/{{seriesId}}/manuscripts/{{manuscriptId}}": {
            "GET": (
                "Displays the manuscript with manuscript id {{manuscriptId}} "
                + "that is in the series with series id {{seriesId}}."
            ),
            "PATCH": (
                "Updates the manuscript with manuscript id {{manuscriptId}}, "
                + "that is part of the series with series id {{seriesId}}, "
                + "according to the data submitted."
            ),
        },
    },
}


@blueprint.route("", methods=["GET"])
def docroot():
    """
    Returns a json object that outlines all 83 other endpoints in the
    interface with brief help text for each.
    """
    try:
        return jsonify(HELP_JSOBJ)
    except Exception as exception:
        return handle_exc(exception)
