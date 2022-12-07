#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('salespeople', __name__, url_prefix='/salespeople')


# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Salesperson class. By wrapping it in a
# zero-argument lambda, the embedded request.args variable isn't evaluated until
# the function is called within the context of an endpoint function.
salesperson_update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                             'last_name': (str, (), request.args.get('last_name')),
                                             'salary': (str, (), request.args.get('salary'))}

# This lambda holds the dict needed as an argument to create_model_obj() or
# update_model_obj() when called for the Client class. By wrapping it in a
# zero-argument lambda, the embedded request.args variable isn't evaluated until
# the function is called within the context of an endpoint function.
client_update_or_create_args = lambda: {'email_address': (str, (), request.args.get('email_address')),
                                        'phone_number': (str, (11, 11), request.args.get('phone_number')),
                                        'business_name': (str, (), request.args.get('business_name')),
                                        'street_address': (str, (), request.args.get('street_address')),
                                        'city': (str, (), request.args.get('city')),
                                        'state_or_province': (str, (2, 4), request.args.get('state_or_province')),
                                        'zipcode': (str, (9, 9), request.args.get('zipcode')),
                                        'country': (str, (), request.args.get('country'))}


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /salespeople endpoint. All rows in the salespeople table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    try:
        result = [salesperson_obj.serialize() for salesperson_obj in Salesperson.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>', methods=['GET'])
def show_salesperson(salesperson_id: int):
    """
    Implements a GET /salespeople/<id> endpoint. The row in the salespeople
    table with the given salesperson_id is loaded and output in JSON.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     load and display.
    :return:         A flask.Response object.
    """
    try:
        salesperson_obj = Salesperson.query.get_or_404(salesperson_id)
        return jsonify(salesperson_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>/clients', methods=['GET'])
def show_salesperson_clients(salesperson_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        retval = [client_obj.serialize() for client_obj in Client.query.where(Client.salesperson_id == salesperson_id)]
        if not len(retval):
            return abort(404)
        return jsonify(retval)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['GET'])
def show_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a GET /salespeople/<id>/clients endpoint. All rows in the clients
    table with that salesperson_id are loaded and output as a JSON list.

    :salesperson_id: The salesperson_id of the rows from the clients table to
                     display.
    :return:    A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        client_objs = list(Client.query.where(Client.salesperson_id == salesperson_id))
        for client_obj in client_objs:
            if client_obj.client_id == client_id:
                return jsonify(client_obj.serialize())
        return abort(404)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_salesperson():
    """
    Implements a POST /salespeople endpoint. A new row in the salespeople table
    is constituted from the CGI parameters and saved to that table.

    :return:    A flask.Response object.
    """
    try:
        salesperson_obj = create_model_obj(Salesperson, salesperson_update_or_create_args())
        db.session.add(salesperson_obj)
        db.session.commit()
        return jsonify(salesperson_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>/clients', methods=['POST'])
def create_salesperson_client(salesperson_id: int):
    """
    Implements a POST /salespeople/<id>/<id>/clients endpoint. A new row in the
    clients table is constituted from the CGI parameters and that salesperson_id
    and saved to that table.

    :salesperson_id: The salesperson_id to save to the new row in the clients
                     table.
    :client_id:      The client_id of the row in the clients table to update.
    :return:         A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        client_obj = create_model_obj(Client, client_update_or_create_args())
        client_obj.salesperson_id = salesperson_id
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>', methods=['PATCH'])
def update_salesperson(salesperson_id: int):
    """
    Implements a PATCH /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is updated from the CGI parameters.

    :salesperson_id: The salesperson_id of the row in the salespeople table to
                     update.
    :return:         A flask.Response object.
    """
    try:
        salesperson_obj = update_model_obj(salesperson_id, Salesperson, salesperson_update_or_create_args())
        db.session.add(salesperson_obj)
        db.session.commit()
        return jsonify(salesperson_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>/clients/<int:client_id>', methods=['PATCH'])
def update_salesperson_client_by_id(salesperson_id: int, client_id: int):
    """
    Implements a PATCH /salespeople/<id>/clients/<id> endpoint. The row in the
    clients table with that client_id and that salesperson_id is updated from
    the CGI parameters.

    :salesperson_id: The salesperson_id of the row in the clients table to
                     update.
    :client_id:      The client_id of the row in the clients table to update.
    :return:         A flask.Response object.
    """
    try:
        Salesperson.query.get_or_404(salesperson_id)
        if not any(client_obj.client_id == client_id for client_obj in Client.query.where(Client.salesperson_id == salesperson_id)):
            return abort(404)
        client_obj = update_model_obj(client_id, Client, client_update_or_create_args())
        client_obj.salesperson_id = salesperson_id
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:salesperson_id>', methods=['DELETE'])
def delete_salesperson(salesperson_id: int):
    """
    Implements a DELETE /salespeople/<id> endpoint. The row in the salespeople
    table with that salesperson_id is deleted.

    :salesperson_id: The salesperson_id of the row in the salespeople table to delete.
    :return:         A flask.Response object.
    """
    try:
        delete_model_obj(salesperson_id, Salesperson)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


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
    try:
        Salesperson.query.get_or_404(salesperson_id)
        if not any(client_obj.client_id == client_id for client_obj in Client.query.where(Client.salesperson_id == salesperson_id)):
            return abort(404)
        delete_model_obj(client_id, Client)
        return jsonify(True)
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
