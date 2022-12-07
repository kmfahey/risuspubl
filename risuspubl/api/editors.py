#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('editors', __name__, url_prefix='/editors')


update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                 'last_name': (str, (), request.args.get('last_name')),
                                 'salary': (int, (), request.args.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    try:
        result = [editor_obj.serialize() for editor_obj in Editor.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['GET'])
def show_editor(editor_id: int):
    try:
        editor_obj = Editor.query.get_or_404(editor_id)
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('', methods=['POST'])
def create_editor():
    try:
        editor_obj = create_model_obj(Editor, update_or_create_args())
        db.session.add(editor_obj)
        db.session.commit()
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['PATCH'])
def update_editor(editor_id: int):
    try:
        editor_obj = update_model_obj(editor_id, Editor, update_or_create_args())
        db.session.add(editor_obj)
        db.session.commit()
        return jsonify(editor_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor(editor_id: int):
    try:
        delete_model_obj(editor_id, Editor)
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
