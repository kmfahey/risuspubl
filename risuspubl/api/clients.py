#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.api.endpfact import delete_class_obj_by_id_factory, update_class_obj_by_id_factory, \
        create_class_obj_factory, show_class_obj_by_id, show_class_index
from risuspubl.dbmodels import *


blueprint = Blueprint('clients', __name__, url_prefix='/clients')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Client class. By wrapping it in a
# zero-argument lambda, the embedded request.json variable isn't evaluated until
# the function is called within the context of an endpoint function.
update_or_create_args = lambda: {'salesperson_id':      (int, (0,),     request.json.get('salesperson_id')),
                                 'email_address':       (str, (),       request.json.get('email_address')),
                                 'phone_number':        (str, (11, 11), request.json.get('phone_number')),
                                 'business_name':       (str, (),       request.json.get('business_name')),
                                 'street_address':      (str, (),       request.json.get('street_address')),
                                 'city':                (str, (),       request.json.get('city')),
                                 'state_or_province':   (str, (2, 4),   request.json.get('state_or_province')),
                                 'zipcode':             (str, (9, 9),   request.json.get('zipcode')),
                                 'country':             (str, (),       request.json.get('country'))}


clients_indexer = show_class_index(Client)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /clients endpoint. All rows in the clients table are loaded
    and output as a JSON list.

    :return: A flask.Response object.
    """
    return clients_indexer()


client_by_id_shower = show_class_obj_by_id(Client)


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


client_creator = create_class_obj_factory(Client)


@blueprint.route('', methods=['POST'])
def create_client():
    """
    Implements a POST /clients endpoint. A new row in the clients table is
    constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return client_creator(request.json)


client_by_id_updater = update_class_obj_by_id_factory(Client, 'client_id')


@blueprint.route('/<int:client_id>', methods=['PATCH', 'PUT'])
def update_client_by_id(client_id: int):
    """
    Implements a PATCH /clients/<id> endpoint. The row in the clients table with
    that client_id is updated from the JSON parameters.

    :client_id: The client_id of the row in the clients table to update.
    :return:    A flask.Response object.
    """
    return client_by_id_updater(client_id, request.json)


client_by_id_deleter = delete_class_obj_by_id_factory(Client, 'client_id')


@blueprint.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id: int):
    """
    Implements a DELETE /clients/<id> endpoint. The row in the clients table
    with that client_id is deleted.

    :client_id: The client_id of the row in the clients table to delete.
    :return:    A flask.Response object.
    """
    return client_by_id_deleter(client_id)
