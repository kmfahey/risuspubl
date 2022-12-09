#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, request

from risuspubl.api.utility import create_table_row, delete_table_row_by_id, display_table_rows, \
        display_table_row_by_id, update_table_row_by_id
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
create_client = create_table_row(Client)
delete_client_by_id = delete_table_row_by_id(Client, 'client_id')
display_client_by_id = display_table_row_by_id(Client)
display_clients = display_table_rows(Client)
update_client_by_id = update_table_row_by_id(Client, 'client_id')


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /clients endpoint. All rows in the clients table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return display_clients()


@blueprint.route('/<int:client_id>', methods=['GET'])
def show_client_by_id(client_id: int):
    """
    Implements a GET /clients/<id> endpoint. The row in the clients table with
    the given client_id is loaded and output in JSON.

    :client_id: The client_id of the row in the clients table to load and
                display.
    :return:    A flask.Response object.
    """
    return display_client_by_id(client_id)


@blueprint.route('', methods=['POST'])
def create_client():
    """
    Implements a POST /clients endpoint. A new row in the clients table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return create_client(request.json)


@blueprint.route('/<int:client_id>', methods=['PATCH', 'PUT'])
def update_client_by_id(client_id: int):
    """
    Implements a PATCH /clients/<id> endpoint. The row in the clients table with
    that client_id is updated from the JSON parameters.

    :client_id: The client_id of the row in the clients table to update.
    :return:    A flask.Response object.
    """
    return update_client_by_id(client_id, request.json)


@blueprint.route('/<int:client_id>', methods=['DELETE'])
def delete_client_by_id(client_id: int):
    """
    Implements a DELETE /clients/<id> endpoint. The row in the clients table
    with that client_id is deleted.

    :client_id: The client_id of the row in the clients table to delete.
    :return:    A flask.Response object.
    """
    return delete_client_by_id(client_id)
