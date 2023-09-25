#!/usr/bin/python3

from flask import Blueprint, jsonify, request

from risuspubl.api.utility import (
    create_model_obj,
    create_table_row_function,
    delete_table_row_by_id_function,
    delete_table_row_by_id_and_foreign_key_function,
    display_table_row_by_id_function,
    display_table_row_by_id_and_foreign_key_function,
    display_table_rows_function,
    display_table_rows_by_foreign_id_function,
    generate_create_update_argd,
    handle_exception,
    update_table_row_by_id_function,
    update_table_row_by_id_and_foreign_key_function,
)
from risuspubl.dbmodels import Client, Salesperson, db


blueprint = Blueprint("salespeople", __name__, url_prefix="/salespeople")


# These functions return closures that implement the requested functions,
# filling in the blank(s) with the provided class objects.
create_salesperson = create_table_row_function(Salesperson)
delete_client_by_client_id_and_salesperson_id = (
    delete_table_row_by_id_and_foreign_key_function(
        Salesperson, "salesperson_id", Client, "client_id"
    )
)
delete_salesperson_by_id = delete_table_row_by_id_function(Salesperson)
display_client_by_client_id_and_salesperson_id = (
    display_table_row_by_id_and_foreign_key_function(
        Salesperson, "salesperson_id", Client, "client_id"
    )
)
display_clients_by_salesperson_id = display_table_rows_by_foreign_id_function(
    Salesperson, "salesperson_id", Client
)
display_salespeople = display_table_rows_function(Salesperson)
display_salesperson_by_id = display_table_row_by_id_function(Salesperson)
update_client_by_client_id_and_salesperson_id = (
    update_table_row_by_id_and_foreign_key_function(
        Salesperson, "salesperson_id", Client, "client_id"
    )
)
update_salesperson_by_id = update_table_row_by_id_function(Salesperson)


@blueprint.route("", methods=["GET"])
def index_endpoint():
    """
    Implements a GET /salespeople endpoint. All rows in the salespeople table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    try:
        return display_salespeople()
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>", methods=["GET"])
def display_salesperson_by_id_endpoint(salesperson_id: int):
    """
    Implements a GET /salespeople/{salesperson_id} endpoint. The row in the
    salespeople table with the given salesperson_id is loaded and output in
    JSON.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     load and display.
    :return:         A flask.Response object.
    """
    try:
        return display_salesperson_by_id(salesperson_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>/clients", methods=["GET"])
def display_salesperson_clients_endpoint(salesperson_id: int):
    """
    Implements a GET /salespeople/{salesperson_id}/clients endpoint. All rows in
    the clients table with that salesperson_id are loaded and output as a JSON
    list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    try:
        return display_clients_by_salesperson_id(salesperson_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>/clients/<int:client_id>", methods=["GET"])
def display_salesperson_client_by_id_endpoint(salesperson_id: int, client_id: int):
    """
    Implements a GET /salespeople/{salesperson_id}/clients endpoint. All rows in
    the clients table with that salesperson_id are loaded and output as a JSON
    list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    try:
        return display_client_by_client_id_and_salesperson_id(salesperson_id, client_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("", methods=["POST"])
def create_salesperson_endpoint():
    """
    Implements a POST /salespeople endpoint. A new row in the salespeople table
    is constituted from the JSON parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        return create_salesperson(request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>/clients", methods=["POST"])
def create_salesperson_client_endpoint(salesperson_id: int):
    """
    Implements a POST /salespeople/{salesperson_id}/clients endpoint. A new
    row in the clients table is constituted from the JSON parameters and that
    salesperson_id and saved to that table.

    :salesperson_id: The salesperson_id to save to the new row in the clients
                     table.
    :return:         A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        # Using create_model_obj() to process request.json into a Client()
        # argument dict and instance a Client() object.
        client_obj = create_model_obj(
            Client,
            generate_create_update_argd(
                Client, request.json, salesperson_id=salesperson_id
            ),
        )
        client_obj.salesperson_id = salesperson_id
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>", methods=["PATCH", "PUT"])
def update_salesperson_by_id_endpoint(salesperson_id: int):
    """
    Implements a PATCH /salespeople/{salesperson_id} endpoint. The row in
    the salespeople table with that salesperson_id is updated from the JSON
    parameters.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     update.
    :return:         A flask.Response object.
    """
    try:
        return update_salesperson_by_id(salesperson_id, request.json)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route(
    "/<int:salesperson_id>/clients/<int:client_id>", methods=["PATCH", "PUT"]
)
def update_salesperson_client_by_id_endpoint(salesperson_id: int, client_id: int):
    """
    Implements a PATCH /salespeople/{salesperson_id}/clients/{client_id}
    endpoint. The row in the clients table with that client_id and that
    salesperson_id is updated from the JSON parameters.

    :salesperson_id: The salesperson_id of the row in the clients table to
                     update.
    :client_id:      The client_id of the row in the clients table to update.
    :return:         A flask.Response object.
    """
    try:
        return update_client_by_client_id_and_salesperson_id(
            salesperson_id, client_id, request.json
        )
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>", methods=["DELETE"])
def delete_salesperson_by_id_endpoint(salesperson_id: int):
    """
    Implements a DELETE /salespeople/{salesperson_id} endpoint. The row in the
    salespeople table with that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the salespeople table to delete.
    :return:         A flask.Response object.
    """
    try:
        return delete_salesperson_by_id(salesperson_id)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route("/<int:salesperson_id>/clients/<int:client_id>", methods=["DELETE"])
def delete_salesperson_client_by_id_endpoint(salesperson_id: int, client_id: int):
    """
    Implements a DELETE /salespeople/{salesperson_id}/clients/{client_id}
    endpoint. The row in the clients table with that client_id and that
    salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the clients table to
                     delete.
    :client_id:      The client_id value of the row in the clients table to
                     delete.
    :return:         A flask.Response object.
    """
    try:
        return delete_client_by_client_id_and_salesperson_id(salesperson_id, client_id)
    except Exception as exception:
        return handle_exception(exception)
