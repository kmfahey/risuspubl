#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('series', __name__, url_prefix='/series')


update_or_create_args = lambda: {'title': (str, (), request.args.get('title')),
                                 'volumes': (int, (2, 5), request.args.get('volumes'))}


@blueprint.route('', methods=['GET'])
def index():
    result = [series_obj.serialize() for series_obj in Series.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series(series_id: int):
    series_obj = Series.query.get_or_404(series_id)
    return jsonify(series_obj.serialize())


@blueprint.route('', methods=['POST'])
def create_series():
    try:
        series_obj = create_model_obj(Series, update_or_create_args())
    except ValueError as exception:
        return Response(exception.args[0], status=400) if len(exception.args) else abort(400)
    db.session.add(series_obj)
    db.session.commit()
    return jsonify(series_obj.serialize())


@blueprint.route('/<int:series_id>', methods=['PATCH'])
def update_series(series_id: int):
    try:
        series_obj = update_model_obj(series_id, Series, update_or_create_args())
    except ValueError as exception:
        return Response(exception.args[0], status=400) if len(exception.args) else abort(400)
    db.session.add(series_obj)
    db.session.commit()
    return jsonify(series_obj.serialize())


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    delete_model_obj(series_id, Series)
    return jsonify(True)
