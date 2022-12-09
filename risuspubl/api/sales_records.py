#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, Response, abort, jsonify

from risuspubl.api.endpfact import show_class_obj_by_id
from risuspubl.dbmodels import SalesRecord


blueprint = Blueprint('sales_records', __name__, url_prefix='/sales_records')


# This is a callable object being instanced from classes imported from
# risuspubl.api.endpfact. See that module for the classes.
sales_record_by_id_shower = show_class_obj_by_id(SalesRecord)


@blueprint.route('/<int:sales_record_id>', methods=['GET'])
def show_sales_record(sales_record_id: int):
    """
    Implements a GET /<id> endpoint. The row with that sales_record_id in the
    sales_records table is loaded and output as JSON.

    :year:   The year of rows from sales_records table to display.
    :return: A flask.Response object.
    """
    return sales_record_by_id_shower(sales_record_id)


@blueprint.route('/year/<int:year>', methods=['GET'])
def show_sales_records_by_year(year: int):
    """
    Implements a GET /year/<year> endpoint. All rows in the sales_records table
    with that year are loaded and output as a JSON list.

    :year:   The year of rows from sales_records table to display.
    :return: A flask.Response object.
    """
    try:
        retval = list()
        if not (1990 <= year <= 2022):
            raise ValueError(f'year parameter value {year} not in the range [1990, 2022]: no sales in specified year')
        for sales_record_obj in SalesRecord.query.where(SalesRecord.year == year):
            retval.append(sales_record_obj.serialize())
        retval.sort(key=lambda dictval: (dictval['month'], dictval['book_id']))
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/year/<int:year>/month/<int:month>', methods=['GET'])
def show_sales_records_by_year_and_month(year: int, month: int):
    """
    Implements a GET /year/<year>/month/<month> endpoint. All rows in the
    sales_records table with that year and that month are loaded and output as a
    JSON list.

    :year:   The year of rows from sales_records table to display.
    :month:  The year of rows from sales_records table to display.
    :return: A flask.Response object.
    """
    try:
        retval = list()
        if not (1990 <= year <= 2022):
            raise ValueError(f'year parameter value {year} not in the range [1990, 2022]: no sales in specified year')
        elif not (1 <= month <= 12):
            raise ValueError(f'month parameter value {month} not in the range [1, 12]: invalid month parameter')
        for sales_record_obj in SalesRecord.query.where(SalesRecord.year == year).where(SalesRecord.month == month):
            retval.append(sales_record_obj.serialize())
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                if len(exception.args) else abort(status))


# Adding, updating and deleting sales records is deliberately made impossible
# since that's outside their object model: each book has sales records for every
# month between its publication date and present, or the date it went out of
# print if it's out of print. New records are generated in bulk at the end of
# each month. If a record were to be removed, the entire sales history for that
# book would be impaired. Records aren't just added or removed at any time,
# and the way they're added in bulk at end-of-month isn't done by a RESTful
# algorithm, you use SQL to INSERT from a csv for that. So records are read-only.
