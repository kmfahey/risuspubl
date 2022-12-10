#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import delete_table_row_by_id, display_table_row_by_id, display_table_rows, \
        update_table_row_by_id
from risuspubl.dbmodels import Manuscript


blueprint = Blueprint('manuscripts', __name__, url_prefix='/manuscripts')


# These are callable objects-- functions with state-- instanced from
# risuspubl.api.utility.endpoint_action subclasses. See that module for the
# classes. Each implements a common design pattern in the endpoint functions
# this package implements.
delete_manuscript_by_id = delete_table_row_by_id(Manuscript)
display_manuscript_by_id = display_table_row_by_id(Manuscript)
display_manuscripts = display_table_rows(Manuscript)
update_manuscript_by_Id = update_table_row_by_id(Manuscript)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return display_manuscripts()


@blueprint.route('/<int:manuscript_id>', methods=['GET'])
def show_manuscript_by_id(manuscript_id: int):
    """
    Implements a GET /manuscripts/<id> endpoint. The row in the manuscripts
    table with the given manuscript_id is loaded and output in JSON.

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
def update_manuscript_by_id(manuscript_id: int):
    """
    Implements a PATCH /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is updated from the JSON parameters.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    return update_manuscript_by_Id(manuscript_id, request.json)


@blueprint.route('/<int:manuscript_id>', methods=['DELETE'])
def delete_manuscript_by_id(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    return delete_manuscript_by_id(manuscript_id)
