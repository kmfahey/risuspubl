#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools
import re

from datetime import date

from flask import Blueprint, jsonify, request, Response, abort

from risuspubl.dbmodels import *
from risuspubl.api.commons import *



blueprint = Blueprint('editors', __name__, url_prefix='/editors')


update_or_create_args = lambda: {'first_name': (str, (), request.args.get('first_name')),
                                 'last_name': (str, (), request.args.get('last_name')),
                                 'salary': (int, (), request.args.get('salary'))}


@blueprint.route('', methods=['GET'])
def index():
    result = [editor_obj.serialize() for editor_obj in Editor.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:editor_id>', methods=['GET'])
def show_editor(editor_id: int):
    editor_obj = Editor.query.get_or_404(editor_id)
    return jsonify(editor_obj.serialize())


@blueprint.route('', methods=['POST'])
def create_editor():
    editor_obj = create_model_obj(Editor, update_or_create_args())
    db.session.add(editor_obj)
    db.session.commit()
    return jsonify(editor_obj.serialize())


@blueprint.route('/<int:editor_id>', methods=['PATCH'])
def update_editor(editor_id: int):
    try:
        editor_obj = update_model_obj(editor_id, Editor, update_or_create_args())
    except ValueError:
        return abort(400)
    db.session.add(editor_obj)
    db.session.commit()
    return jsonify(editor_obj.serialize())


@blueprint.route('/<int:editor_id>', methods=['DELETE'])
def delete_editor(editor_id: int):
    try:
        delete_model_obj(editor_id, Editor)
    except:
        return abort(400)
    return jsonify(True)
