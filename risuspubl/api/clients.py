#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools
import re

from datetime import date

from flask import Blueprint, jsonify, request, Response, abort

from risuspubl.dbmodels import *
from risuspubl.api.commons import *



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
    result = [client_obj.serialize() for client_obj in Client.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:client_id>', methods=['GET'])
def show_client(client_id: int):
    client_obj = Client.query.get_or_404(client_id)
    return jsonify(client_obj.serialize())


@blueprint.route('', methods=['POST'])
def create_client():
    client_obj = create_model_obj(Client, update_or_create_args())
    db.session.add(client_obj)
    db.session.commit()
    return jsonify(client_obj.serialize())


@blueprint.route('/<int:client_id>', methods=['PATCH'])
def update_client(client_id: int):
    if 'title' in request.args:
        if len(tuple(Client.query.where(Client.title == request.args['title']))):
            return abort(400)
    try:
        client_obj = update_model_obj(client_id, Client, update_or_create_args())
    except ValueError:
        return abort(400)
    db.session.add(client_obj)
    db.session.commit()
    return jsonify(client_obj.serialize())


@blueprint.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id: int):
    try:
        delete_model_obj(client_id, Client)
    except:
        return abort(400)
    return jsonify(True)
