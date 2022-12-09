#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import delete_class_obj_by_id_factory, show_class_index, show_class_obj_by_id, \
        update_class_obj_by_id_factory
from risuspubl.dbmodels import Manuscript


blueprint = Blueprint('manuscripts', __name__, url_prefix='/manuscripts')


# These are callable objects being instanced from classes imported from
# risuspubl.api.utility. See that module for the classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
manuscript_by_id_deleter = delete_class_obj_by_id_factory(Manuscript, 'manuscript_id')
manuscript_by_id_shower = show_class_obj_by_id(Manuscript)
manuscript_by_id_updater = update_class_obj_by_id_factory(Manuscript, 'manuscript_id')
manuscripts_indexer = show_class_index(Manuscript)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return manuscripts_indexer()


@blueprint.route('/<int:manuscript_id>', methods=['GET'])
def show_manuscript_by_id(manuscript_id: int):
    """
    Implements a GET /manuscripts/<id> endpoint. The row in the manuscripts
    table with the given manuscript_id is loaded and output in JSON.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    return manuscript_by_id_shower(manuscript_id)


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
    return manuscript_by_id_updater(manuscript_id, request.json)


@blueprint.route('/<int:manuscript_id>', methods=['DELETE'])
def delete_manuscript_by_id(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    return manuscript_by_id_deleter(manuscript_id)
