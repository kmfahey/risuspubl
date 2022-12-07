#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('series', __name__, url_prefix='/series')


update_or_create_args = lambda: {'title': (str, (), request.args.get('title')),
                                 'volumes': (int, (2, 5), request.args.get('volumes'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [series_obj.serialize() for series_obj in Series.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['GET'])
def show_series(series_id: int):
    try:
        series_obj = Series.query.get_or_404(series_id)
        return jsonify(series_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_series():
    try:
        series_obj = create_model_obj(Series, update_or_create_args())
        db.session.add(series_obj)
        db.session.commit()
        return jsonify(series_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['PATCH'])
def update_series(series_id: int):
    try:
        series_obj = update_model_obj(series_id, Series, update_or_create_args())
        db.session.add(series_obj)
        db.session.commit()
        return jsonify(series_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    try:
        delete_model_obj(series_id, Series)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
