#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from flask import Blueprint, jsonify

from risuspubl.api.utility import display_table_row_by_id_function, handle_exception
from risuspubl.dbmodels import SalesRecord


blueprint = Blueprint('sales_records', __name__, url_prefix='/sales_records')


# This function returns a closure that implements the requested function,
# filling in the blank with the provided class object.
display_sales_record_by_id = display_table_row_by_id_function(SalesRecord)


@blueprint.route('/<int:sales_record_id>', methods=['GET'])
def display_sales_record_endpoint(sales_record_id: int):
    """
    Implements a GET /sales_records/{sales_record_id} endpoint. The row with
    that sales_record_id in the sales_records table is displayed.

    :year:   The year of rows from sales_records table to display.
    :return: A flask.Response object.
    """
    return display_sales_record_by_id(sales_record_id)


@blueprint.route('/years/<int:year>', methods=['GET'])
def display_sales_records_by_year_endpoint(year: int):
    """
    Implements a GET /sales_records/years/{year} endpoint. All rows in the
    sales_records table with that year are displayed in order by year, month and
    book_id.

    :year:   The year of rows from sales_records table to display.
    :return: A flask.Response object.
    """
    retval = list()
    if not (1990 <= year <= 2022):
        raise ValueError(f'year parameter value {year} not in the range [1990, 2022]: no sales in specified year')
    for sales_record_obj in SalesRecord.query.where(SalesRecord.year == year):
        retval.append(sales_record_obj.serialize())
    retval.sort(key=lambda dictval: (dictval['year'], dictval['month'], dictval['book_id']))
    return jsonify(retval)


@blueprint.route('/years/<int:year>/month/<int:month>', methods=['GET'])
def display_sales_records_by_year_and_month_endpoint(year: int, month: int):
    """
    Implements a GET /sales_records/years/{year}/month/{month} endpoint. All rows in the
    sales_records table with that year and that month are loaded and output as a
    JSON list.

    :year:   The year of rows from sales_records table to display (between 1990
             and the current year).
    :month:  The month of rows from sales_records table to display (between 1
             and 12).
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
        retval.sort(key=lambda dictval: (dictval['year'], dictval['month'], dictval['book_id']))
        return jsonify(retval)
    except Exception as exception:
        return handle_exception(exception)


@blueprint.route('/books/<int:book_id>', methods=['GET'])
def display_sales_records_by_book_id_endpoint(book_id: int):
    """
    Implements a GET /sales_records/books/{book_id} endpoint. All rows in the
    sales_records table with that book_id value are displayed in order by year
    and month.

    :book_id: The book_id of the book to see the complete sales records for.
    :return:  a flask.Response object
    """
    sales_record_objs = tuple(SalesRecord.query.where(SalesRecord.book_id == book_id))
    if len(sales_record_objs) == 0:
        return abort(404)
    retval = [sales_record_obj.serialize() for sales_record_obj in sales_record_objs]
    retval.sort(key=lambda dictval: (dictval['year'], dictval['month']))
    return jsonify(retval)


@blueprint.route('/years/<int:year>/books/<int:book_id>', methods=['GET'])
def display_sales_records_by_year_and_book_id_endpoint(year: int, book_id: int):
    """
    Implements a GET /sales_records/years/{year}/books/{book_id} endpoint. Loads
    the sales data from the sales_records table for the specified year and the
    specified book and displays them in order by month.

    :year:    the year to retrieve sales data for
    :book_id: the book_id of the book to retrieve sales data for
    :return:  a flask.Response object
    """
    sales_record_objs = tuple(SalesRecord.query.where(SalesRecord.book_id == book_id)
                                               .where(SalesRecord.year == year))
    if len(sales_record_objs) == 0:
        return abort(404)
    retval = [sales_record_obj.serialize() for sales_record_obj in sales_record_objs]
    retval.sort(key=lambda dictval: (dictval['year'], dictval['month']))
    return jsonify()


@blueprint.route('/years/<int:year>/months/<int:month>/books/<int:book_id>', methods=['GET'])
def display_sales_records_by_year_and_month_and_book_id_endpoint(year: int, month: int, book_id: int):
    """
    Implements a GET /sales_records/years/{year}/months/{month}/books/{book_id}
    endpoint. Retrieves the row in the sales_records table with the given year,
    month and book_id values and displays it.

    :year: the year to retrieve sales data for
    :month: the month to retrieve sales data for
    :book_id: the book_id to retrieve sales data for
    :return:    a flask.Response object
    """
    sales_record_objs = tuple(SalesRecord.query.where(SalesRecord.book_id == book_id)
                                               .where(SalesRecord.year == year)
                                               .where(SalesRecord.month == month))
    if len(sales_record_objs) == 0:
        return abort(404)
    sales_record_obj, = sales_record_objs
    return jsonify(sales_record_obj.serialize())



# Adding, updating and deleting sales records is deliberately made impossible
# since that's outside their object model: each book has sales records for
# every month between its publication date and present, or the date it went
# out of print if it's out of print. New records are generated in bulk at the
# end of each month. If a record were to be removed, the entire sales history
# for that book would be impaired. Records aren't just added or removed at
# any time, and the way they're added in bulk at end-of-month isn't done by a
# RESTful algorithm, you use SQL to INSERT from a csv for that. So records are
# read-only.
