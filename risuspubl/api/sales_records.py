#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

import itertools
import re

from datetime import date

from flask import Blueprint, jsonify, request, Response, abort

from risuspubl.dbmodels import *
from risuspubl.api.commons import *



blueprint = Blueprint('sales_records', __name__, url_prefix='/sales_records')


update_or_create_args = lambda: {'sales_record_id', (int, (0,), request.args.get('sales_record_id')),
                                 'book_id', (int, (0,), request.args.get('book_id')),
                                 'year', (int, (1900, 2022), request.args.get('year')),
                                 'month', (int, (1, 12), request.args.get('month')),
                                 'copies_sold', (int, (1,), request.args.get('copies_sold')),
                                 'gross_profit', (float, (0.01,), request.args.get('gross_profit')),
                                 'net_profit', (float, (0.01,), request.args.get('net_profit'))}


@blueprint.route('', methods=['GET'])
def index():
    result = [sales_record_obj.serialize() for sales_record_obj in SalesRecord.query.all()]
    return jsonify(result) # return JSON response


@blueprint.route('/<int:sales_record_id>', methods=['GET'])
def show_sales_record(sales_record_id: int):
    sales_record_obj = SalesRecord.query.get_or_404(sales_record_id)
    return jsonify(sales_record_obj.serialize())


# Adding, updating and deleting sales records is deliberately made impossible
# since that's outside their object model: each book has sales records for every
# month between its publication date and present, or the date it went out of
# print if it's out of print. New records are generated in bulk at the end of
# each month. If a record were to be removed, the entire sales history for that
# book would be impaired. Records aren't just added or removed at any time,
# and the way they're added in bulk at end-of-month isn't done by a RESTful
# algorithm, you use SQL to INSERT from a csv for that. So records are read-only.
