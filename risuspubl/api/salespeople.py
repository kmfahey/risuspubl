#!/home/kmfahey/Workspace/NuCampFolder/Python/1-SQL/week3/venv/bin/python3

from flask import Blueprint, Response, abort, jsonify, request

import werkzeug.exceptions

from risuspubl.api.utility import create_model_obj, create_or_update_argd_gen, create_table_row, \
        delete_table_row_by_id, delete_table_row_by_id_w_foreign_key, display_table_row_by_id, \
        display_table_row_by_id_w_foreign_key, display_table_rows, display_table_rows_w_foreign_id, \
        update_table_row_by_id, update_table_row_by_id_w_foreign_key
from risuspubl.dbmodels import Client, Salesperson, db


blueprint = Blueprint('salespeople', __name__, url_prefix='/salespeople')


# These are callable objects being instanced from classes imported from
# risuspubl.api.utility. See that module for the classes.
#
# These callables were derived from duplicated code across the risuspubl.api.*
# codebase. Each one implements the entirety of a specific endpoint function,
# such that an endpoint function just tail calls the corresponding one of
# these callables. The large majority of code reuse was eliminated by this
# refactoring.
create_salesperson = create_table_row(Salesperson)
delete_client_by_client_id_and_salesperson_id = delete_table_row_by_id_w_foreign_key(Salesperson, 'salesperson_id',
                                                                                     Client, 'client_id')
delete_salesperson_by_id = delete_table_row_by_id(Salesperson, 'salesperson_id')
display_client_by_client_id_and_salesperson_id = display_table_row_by_id_w_foreign_key(Salesperson, 'salesperson_id',
                                                                                       Client, 'client_id')
display_clients_by_salesperson_id = display_table_rows_w_foreign_id(Salesperson, 'salesperson_id', Client)
display_salespeople = display_table_rows(Salesperson)
display_salesperson_by_id = display_table_row_by_id(Salesperson)
update_client_by_client_id_and_salesperson_id = update_table_row_by_id_w_foreign_key(Salesperson, 'salesperson_id',
                                                                                     Client, 'client_id')
update_salesperson_by_id = update_table_row_by_id(Salesperson, 'salesperson_id')


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /salespeople endpoint. All rows in the salespeople table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return display_salespeople()


@blueprint.route('/<int:salesperson_id>', methods=['GET'])
def show_salesperson_by_id(salesperson_id: int):
    """
    Implements a GET /salespeople/<id> endpoint. The row in the salespeople
    table with the given salesperson_id is loaded and output in JSON.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     load and display.
    :return:         A flask.Response object.
    """
    return display_salesperson_by_id(salesperson_id)


@blueprint.route('/<int:salesperson_id>/clients', methods=['GET'])
def show_salesperson_clients(salesperson_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    return display_clients_by_salesperson_id(salesperson_id)


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['GET'])
def show_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    return display_client_by_client_id_and_salesperson_id(salesperson_id, client_id)


@blueprint.route('', methods=['POST'])
def create_salesperson():
    """
    Implements a POST /salespeople endpoint. A new row in the salespeople table
    is constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return create_salesperson(request.json)


@blueprint.route('/<int:salesperson_id>/clients', methods=['POST'])
def create_salesperson_client(salesperson_id: int):
    """
    Implements a POST /salespeople/<id>/<id>/clients endpoint. A new row in the
    clients table is constituted from the JSON parameters and that salesperson_id
    and saved to that table.

    :salesperson_id: The salesperson_id to save to the new row in the clients
                     table.
    :return:         A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        # Using create_model_obj() to process request.json into a Client()
        # argument dict and instance a Client() object.
        client_obj = create_model_obj(Client,
                                      create_or_update_argd_gen(Client, 'salesperson_id')
                                             .generate_argd(request.json, salesperson_id))
        client_obj.salesperson_id = salesperson_id
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        return endpoint_action.handle_exception(exception)


@blueprint.route('/<int:salesperson_id>', methods=['PATCH', 'PUT'])
def update_salesperson_by_id(salesperson_id: int):
    """
    Implements a PATCH /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is updated from the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     update.
    :return:         A flask.Response object.
    """
    return update_salesperson_by_id(salesperson_id, request.json)


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['PATCH', 'PUT'])
def update_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a PATCH /salespeople/<id>/clients/<id> endpoint. The row in the
    clients table with that client_id and that salesperson_id is updated from
    the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the clients table to
                     update.
    :client_id:      The client_id of the row in the clients table to update.
    :return:         A flask.Response object.
    """
    return update_client_by_client_id_and_salesperson_id(salesperson_id, client_id, request.json)


@blueprint.route('/<int:salesperson_id>', methods=['DELETE'])
def delete_salesperson_by_id(salesperson_id: int):
    """
    Implements a DELETE /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the salespeople table to delete.
    :return:         A flask.Response object.
    """
    return delete_salesperson_by_id(salesperson_id)


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['DELETE'])
def delete_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a DELETE /salespeople/<id>/clients/<id> endpoint. The row in the
    clients table with that client_id and that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the clients table to
                     delete.
    :client_id:      The client_id value of the row in the clients table to
                     delete.
    :return:         A flask.Response object.
    """
    return delete_client_by_client_id_and_salesperson_id(salesperson_id, client_id)
