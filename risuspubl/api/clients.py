#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import create_class_obj_factory, delete_class_obj_by_id_factory, show_class_index, \
        show_class_obj_by_id, update_class_obj_by_id_factory
from risuspubl.dbmodels import Client


blueprint = Blueprint('clients', __name__, url_prefix='/clients')


# These are callable objects being instanced from classes imported from
# risuspubl.api.utility. See that module for the classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
client_by_id_deleter = delete_class_obj_by_id_factory(Client, 'client_id')
client_by_id_shower = show_class_obj_by_id(Client)
client_by_id_updater = update_class_obj_by_id_factory(Client, 'client_id')
client_creator = create_class_obj_factory(Client)
clients_indexer = show_class_index(Client)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /clients endpoint. All rows in the clients table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return clients_indexer()


@blueprint.route('/<int:client_id>', methods=['GET'])
def show_client_by_id(client_id: int):
    """
    Implements a GET /clients/<id> endpoint. The row in the clients table with
    the given client_id is loaded and output in JSON.

    :client_id: The client_id of the row in the clients table to load and
                display.
    :return:    A flask.Response object.
    """
    return client_by_id_shower(client_id)


@blueprint.route('', methods=['POST'])
def create_client():
    """
    Implements a POST /clients endpoint. A new row in the clients table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return client_creator(request.json)


@blueprint.route('/<int:client_id>', methods=['PATCH', 'PUT'])
def update_client_by_id(client_id: int):
    """
    Implements a PATCH /clients/<id> endpoint. The row in the clients table with
    that client_id is updated from the JSON parameters.

    :client_id: The client_id of the row in the clients table to update.
    :return:    A flask.Response object.
    """
    return client_by_id_updater(client_id, request.json)


@blueprint.route('/<int:client_id>', methods=['DELETE'])
def delete_client_by_id(client_id: int):
    """
    Implements a DELETE /clients/<id> endpoint. The row in the clients table
    with that client_id is deleted.

    :client_id: The client_id of the row in the clients table to delete.
    :return:    A flask.Response object.
    """
    return client_by_id_deleter(client_id)
