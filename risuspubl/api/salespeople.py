#!/home/kmfahey/Workspace/NuCampFolder/Python/1-SQL/week3/venv/bin/python3

from flask import Blueprint, Response, abort, jsonify, request

import werkzeug.exceptions

from risuspubl.api.utility import create_class_obj_factory, create_model_obj, create_or_update_argd_gen, \
        delete_class_obj_by_id_factory, delete_one_classes_other_class_obj_by_id_factory, \
        show_all_of_one_classes_other_class_objs, show_class_index, show_class_obj_by_id, \
        show_one_classes_other_class_obj_by_id, update_class_obj_by_id_factory, \
        update_one_classes_other_class_obj_by_id_factory
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
salespeople_indexer = show_class_index(Salesperson)
salesperson_by_id_deleter = delete_class_obj_by_id_factory(Salesperson, 'salesperson_id')
salesperson_by_id_shower = show_class_obj_by_id(Salesperson)
salesperson_by_id_updater = update_class_obj_by_id_factory(Salesperson, 'salesperson_id')
salesperson_client_by_id_deleter = delete_one_classes_other_class_obj_by_id_factory(Salesperson, 'salesperson_id',
                                                                                    Client, 'client_id')
salesperson_client_by_id_shower = show_one_classes_other_class_obj_by_id(Salesperson, 'salesperson_id', Client,
                                                                         'client_id')
salesperson_clients_shower = show_all_of_one_classes_other_class_objs(Salesperson, 'salesperson_id', Client)
salesperson_creator = create_class_obj_factory(Salesperson)
series_book_by_id_updater = update_one_classes_other_class_obj_by_id_factory(Salesperson, 'salesperson_id', Client,
                                                                             'client_id')


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /salespeople endpoint. All rows in the salespeople table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return salespeople_indexer()


@blueprint.route('/<int:salesperson_id>', methods=['GET'])
def show_salesperson_by_id(salesperson_id: int):
    """
    Implements a GET /salespeople/<id> endpoint. The row in the salespeople
    table with the given salesperson_id is loaded and output in JSON.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     load and display.
    :return:         A flask.Response object.
    """
    return salesperson_by_id_shower(salesperson_id)


@blueprint.route('/<int:salesperson_id>/clients', methods=['GET'])
def show_salesperson_clients(salesperson_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    return salesperson_clients_shower(salesperson_id)


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['GET'])
def show_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    return salesperson_client_by_id_shower(salesperson_id, client_id)


@blueprint.route('', methods=['POST'])
def create_salesperson():
    """
    Implements a POST /salespeople endpoint. A new row in the salespeople table
    is constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    return salesperson_creator(request.json)


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
        if isinstance(exception, werkzeug.exceptions.NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>', methods=['PATCH', 'PUT'])
def update_salesperson_by_id(salesperson_id: int):
    """
    Implements a PATCH /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is updated from the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     update.
    :return:         A flask.Response object.
    """
    return salesperson_by_id_updater(salesperson_id, request.json)


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
    return series_book_by_id_updater(salesperson_id, client_id, request.json)


@blueprint.route('/<int:salesperson_id>', methods=['DELETE'])
def delete_salesperson_by_id(salesperson_id: int):
    """
    Implements a DELETE /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the salespeople table to delete.
    :return:         A flask.Response object.
    """
    return salesperson_by_id_deleter(salesperson_id)


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
    return salesperson_client_by_id_deleter(salesperson_id, client_id)
