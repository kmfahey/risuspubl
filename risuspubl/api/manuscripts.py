#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('manuscripts', __name__, url_prefix='/manuscripts')


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    try:
        result = [manuscript_obj.serialize() for manuscript_obj in Manuscript.query.all()]
        return jsonify(result) # return JSON response
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:manuscript_id>', methods=['GET'])
def show_manuscript(manuscript_id: int):
    """
    Implements a GET /manuscripts/<id> endpoint. The row in the manuscripts
    table with the given manuscript_id is loaded and output in JSON.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    try:
        manuscript_obj = Manuscript.query.get_or_404(manuscript_id)
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


# A Create endpoint is deliberately not implemented, because without
# a way to specify the author or authors to attach the manuscript to, no
# entry in the authors_manuscripts table would be created and the manuscript
# would an orphan in the database. /authors/<author_id>/manuscripts and
# /authors/<author1_id>/<author2_id>/manuscripts already accept Create actions and
# when done that way associations with an author or authors can be created
# appropriately.


@blueprint.route('/<int:manuscript_id>', methods=['PATCH'])
def update_manuscript(manuscript_id: int):
    """
    Implements a PATCH /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is updated from the CGI parameters.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    try:
        if ('working_title' in request.args
            and len(tuple(Manuscript.query.where(Manuscript.working_title == request.args['working_title'])))):
            # The working_title column in the manuscripts table is required to
            # be unique. If that Manuscript query returns a nonempty sequence,
            # the given value is already in use, so a ValueError is raised.
            raise ValueError(f"'working_title' parameter value '{request.args['working_title']}' already use in a "
                             f'row in the {Manuscript.__tablename__} table; working_title values must be unique')
        # Using update_model_obj() to fetch the manuscript_obj and update it
        # against request.args.
        manuscript_obj = update_model_obj(manuscript_id, Manuscript,
                                          {'editor_id': (int, (0,), request.args.get('editor_id')),
                                           'series_id': (int, (0,), request.args.get('series_id')),
                                           'working_title': (str, (), request.args.get('working_title')),
                                           'due_date': (date, (date.today().isoformat(), '2025-12-31'),
                                                        request.args.get('due_date')),
                                           'advance': (int, (5000, 100000), request.args.get('advance'))})
        db.session.add(manuscript_obj)
        db.session.commit()
        return jsonify(manuscript_obj.serialize())
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/<int:manuscript_id>', methods=['DELETE'])
def delete_manuscript(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    try:
        manuscript_obj = Manuscript.query.get_or_404(manuscript_id)
        # A delete expression for row in the authors_manuscripts table with the
        # given manuscript_id, which need to be deleted as well.
        am_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(am_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
