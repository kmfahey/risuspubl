#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import Blueprint, jsonify, request, Response, abort

from risuspubl.api.commons import *
from risuspubl.dbmodels import *


blueprint = Blueprint('sales_records', __name__, url_prefix='/sales_records')


update_or_create_args = lambda: {'sales_record_id', (int, (0,), request.args.get('sales_record_id')),
                                 'book_id', (int, (0,), request.args.get('book_id')),
                                 'year', (int, (1900, 2022), request.args.get('year')),
                                 'month', (int, (1, 12), request.args.get('month')),
                                 'copies_sold', (int, (1,), request.args.get('copies_sold')),
                                 'gross_profit', (float, (0.01,), request.args.get('gross_profit')),
                                 'net_profit', (float, (0.01,), request.args.get('net_profit'))}



@blueprint.route('/<int:sales_record_id>', methods=['GET'])
def show_sales_record(sales_record_id: int):
    try:
        sales_record_obj = SalesRecord.query.get_or_404(sales_record_id)
        return jsonify(sales_record_obj.serialize())
    except Exception as exception:
        if isinstance(exception, NotFound):
            raise exception from None
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/year/<int:year>', methods=['GET'])
def show_sales_records_by_year(year: int):
    try:
        retval = list()
        if not (1990 <= year <= 2022):
            raise ValueError(f"year parameter value {year} not in the range [1990, 2022]: no sales in specified year")
        for sales_record_obj in SalesRecord.query.where(SalesRecord.year == year):
            retval.append(sales_record_obj.serialize())
        retval.sort(key=lambda dictval: (dictval['month'], dictval['book_id']))
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


@blueprint.route('/year/<int:year>/month/<int:month>', methods=['GET'])
def show_sales_records_by_year_and_month(year: int, month: int):
    try:
        retval = list()
        if not (1990 <= year <= 2022):
            raise ValueError(f"year parameter value {year} not in the range [1990, 2022]: no sales in specified year")
        elif not (1 <= month <= 12):
            raise ValueError(f"month parameter value {month} not in the range [1, 12]: invalid month parameter")
        for sales_record_obj in SalesRecord.query.where(SalesRecord.year == year).where(SalesRecord.month == month):
            retval.append(sales_record_obj.serialize())
        return jsonify(retval)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))


# Adding, updating and deleting sales records is deliberately made impossible
# since that's outside their object model: each book has sales records for every
# month between its publication date and present, or the date it went out of
# print if it's out of print. New records are generated in bulk at the end of
# each month. If a record were to be removed, the entire sales history for that
# book would be impaired. Records aren't just added or removed at any time,
# and the way they're added in bulk at end-of-month isn't done by a RESTful
# algorithm, you use SQL to INSERT from a csv for that. So records are read-only.