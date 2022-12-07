#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('salespeople', __name__, url_prefix='/salespeople')


update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                'last_name': (str, (), request.args.get('last_name')),
                                'salary': (str, (), request.args.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    result = [salesperson_obj.serialize() for salesperson_obj in Salesperson.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:salesperson_id>', methods=['GET'])
def show_salesperson(salesperson_id: int):
    salesperson_obj = Salesperson.query.get_or_404(salesperson_id)
    return jsonify(salesperson_obj.serialize())


@blueprint.route('', methods=['POST'])
def create_salesperson():
    try:
        salesperson_obj = create_model_obj(Salesperson, update_or_create_args())
    except ValueError as exception:
        return Response(exception.args[0], status=400) if len(exception.args) else abort(400)
    db.session.add(salesperson_obj)
    db.session.commit()
    return jsonify(salesperson_obj.serialize())


@blueprint.route('/<int:salesperson_id>', methods=['PATCH'])
def update_salesperson(salesperson_id: int):
    try:
        salesperson_obj = update_model_obj(salesperson_id, Salesperson, update_or_create_args())
    except ValueError as exception:
        return Response(exception.args[0], status=400) if len(exception.args) else abort(400)
    db.session.add(salesperson_obj)
    db.session.commit()
    return jsonify(salesperson_obj.serialize())


@blueprint.route('/<int:salesperson_id>', methods=['DELETE'])
def delete_salesperson(salesperson_id: int):
    delete_model_obj(salesperson_id, Salesperson)
    return jsonify(True)
