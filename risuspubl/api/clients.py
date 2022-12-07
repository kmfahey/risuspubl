#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('clients', __name__, url_prefix='/clients')


update_or_create_args = lambda: {'salesperson_id': (int, (0,), request.args.get('salesperson_id')),
                                 'email_address': (str, (), request.args.get('email_address')),
                                 'phone_number': (str, (11, 11), request.args.get('phone_number')),
                                 'business_name': (str, (), request.args.get('business_name')),
                                 'street_address': (str, (), request.args.get('street_address')),
                                 'city': (str, (), request.args.get('city')),
                                 'state_or_province': (str, (2, 4), request.args.get('state_or_province')),
                                 'zipcode': (str, (9, 9), request.args.get('zipcode')),
                                 'country': (str, (), request.args.get('country'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [client_obj.serialize() for client_obj in Client.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:client_id>', methods=['GET'])
def show_client(client_id: int):
    try:
        client_obj = Client.query.get_or_404(client_id)
        return jsonify(client_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_client():
    try:
        try:
            client_obj = create_model_obj(Client, update_or_create_args())
        except ValueError as exception:
            return (Response(exception.args[0], status=400)
                    if len(exception.args) else abort(400))
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:client_id>', methods=['PATCH'])
def update_client(client_id: int):
    try:
        client_obj = update_model_obj(client_id, Client, update_or_create_args())
        db.session.add(client_obj)
        db.session.commit()
        return jsonify(client_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id: int):
    try:
        delete_model_obj(client_id, Client)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
