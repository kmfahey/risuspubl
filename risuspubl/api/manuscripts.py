#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import delete_table_row_by_id_function, display_table_row_by_id_function, \
        display_table_rows_function, update_table_row_by_id_function
from risuspubl.dbmodels import Manuscript


blueprint = Blueprint('manuscripts', __name__, url_prefix='/manuscripts')


# These functions return closures that implement the requested functions,
# filling in the blank(s) with the provided class objects.
delete_manuscript_by_id = delete_table_row_by_id_function(Manuscript)
display_manuscript_by_id = display_table_row_by_id_function(Manuscript)
display_manuscripts = display_table_rows_function(Manuscript)
update_manuscript_by_Id = update_table_row_by_id_function(Manuscript)


@blueprint.route('', methods=['GET'])
def index_endpoint():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return display_manuscripts()


@blueprint.route('/<int:manuscript_id>', methods=['GET'])
def display_manuscript_by_id_endpoint(manuscript_id: int):
    """
    Implements a GET /manuscripts/{manuscript_id} endpoint. The row in the
    manuscripts table with the given manuscript_id is loaded and output in JSON.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    return display_manuscript_by_id(manuscript_id)


# A Create endpoint is deliberately not implemented, because without a way
# to specify the author or authors to attach the manuscript to, no entry
# in the authors_manuscripts table would be created and the manuscript
# would an orphan in the database. /authors/<author_id>/manuscripts and
# /authors/<author1_id>/<author2_id>/manuscripts already accept Create actions
# and when done that way associations with an author or authors can be created
# appropriately.


@blueprint.route('/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_manuscript_by_id_endpoint(manuscript_id: int):
    """
    Implements a PATCH /manuscripts/{manuscript_id} endpoint. The row in
    the manuscripts table with that manuscript_id is updated from the JSON
    parameters.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    return update_manuscript_by_Id(manuscript_id, request.json)


@blueprint.route('/<int:manuscript_id>', methods=['DELETE'])
def delete_manuscript_by_id_endpoint(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/{manuscript_id} endpoint. The row in the
    manuscripts table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    return delete_manuscript_by_id(manuscript_id)
