#!/usr/bin/python3

import abc
import math
from datetime import date, timedelta

from flask import Response, abort, jsonify

from risuspubl.dbmodels import Author, Authors_Books, Authors_Manuscripts, Book, Client, Editor, Manuscript, \
        SalesRecord, Salesperson, Series, db

import werkzeug.exceptions


# Associates a *_id param name with the SQLAlchemy.Model subclass class object
# representing the table where a column by that name is the primary key. Used to
# validate whether a parameter with such a name has a value that is associated
# with a row in that table.
_foreign_keys_to_model_subclasses = {'book_id': Book, 'client_id': Client, 'editor_id': Editor,
                                     'manuscript_id': Manuscript, 'sales_record_id': SalesRecord,
                                     'salesperson_id': Salesperson, 'series_id': Series}

def create_model_obj(model_subclass, params_argd, optional_params=set()):
    """
    Instantiates an object in the provided SQLAlchemy.Model subclass using the
    dict of key/value pairs as arguments to the constructor. A value in that
    dict can be None if the key is in optional_params, otherwise a ValueError is
    raised. The object is returned.

    :model_subclass:  An SQLAlchemy.Model subclass class object, the class to
                      instance an object of.
    :params_argd:     A dict of parameters key to values.
    :optional_params: An optional argument, a set of parameter names that are
                      not required for the constructor. If the value of one of
                      these parameters is None, it's skipped. If a parameter
                      does NOT occur in this set and it's None, a ValueError is
                      raised.
    :return:          An instance of the class that was the first argument.
    """
    model_obj_args = dict()
    for param_name, param_value in params_argd.items():
        # optional_params is the list of names of parameters that may be None.
        if param_value is None and param_name in optional_params:
            continue
        # If a required param is none, a ValueError is raised.
        elif param_value is None:
            raise ValueError(f"required parameter '{param_name}' not present")
        if param_name.endswith('_id') and param_value is not None:
            # Matching a *_id parameter with the Model class for the table where
            # that column is a primary key, and doing a get() to confirm the *_id
            # value corresponds to a row in that table. If not, a ValueError is
            # raised.
            id_model_subclass = _foreign_keys_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        model_obj_args[param_name] = param_value
    return model_subclass(**model_obj_args)


def update_model_obj(id_val, model_subclass, params_argd):
    """
    Retrieves the object in the SQLAlchemy.Model subclass by the given id, and
    updates it using the dict of key/value pairs to assign new attribute values.
    If a value in the parameter argd is None, it is skipped. The object is
    returned.

    :model_subclass: An SQLAlchemy.Model subclass class object, the class to
                     instance an object of.
    :params_argd:    A dict of parameter keys to values.
    :return:         An instance of the class that was the first argument.
    """
    model_obj = model_subclass.query.get_or_404(id_val)
    # If all the dict's param_value slots are None, this update can't proceed bc
    # there's nothing to update, so a ValueError is raised.
    if all(param_value is None for _, _, param_value in params_argd.values()):
        raise ValueError('update action executed with no parameters indicating fields to update')
    for param_name, param_value in params_argd.items():
        if param_value is None:
            continue
        if param_name.endswith('_id'):
            # Matching a *_id parameters with the Model class for the table
            # where that column is a primary key, and doing a get() to confirm
            # the *_id value corresponds to a row in that table. If not, a
            # ValueError is raised.
            id_model_subclass = _foreign_keys_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        setattr(model_obj, param_name, param_value)
    return model_obj


def delete_model_obj(id_val, model_subclass):
    """
    Looks up an id value in the provided SQLAlchemy.Model subclass, and has
    the matching row in that table deleted. If the model subclass is Book or
    Manuscript, the matching row(s) in authors_books or authors_manuscripts are
    deleted too.

    :id_val:         An int, the value of the id primary key column of the table
                     represented by the model subclass argument.
    :model_subclass: A subclass of SQLAlchemy.Model representing the table to
                     delete a row from.
    :return:         None
    """
    model_obj = model_subclass.query.get_or_404(id_val)
    # In the case of Book or Manuscript objects, there's also corresponding rows
    # in authors_books or authors_manuscripts that need to be deleted as well.
    if model_subclass is Book:
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == id_val)
        db.session.execute(ab_del)
        db.session.commit()
    elif model_subclass is Manuscript:
        am_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == id_val)
        db.session.execute(am_del)
        db.session.commit()
    db.session.delete(model_obj)
    db.session.commit()


def _validate_date(param_name, param_value, lower_bound='1900-01-01', upper_bound=date.today().isoformat()):
    # Parses a param value to a date, and tests if it falls within lower and
    # upper bounds. If it succeeds, the param value string is returned. If
    # it fails, a ValueError is raised.
    if param_value is None:
        return param_value
    try:
        param_date_obj = date.fromisoformat(param_value)
    except ValueError as exception:
        # Attempting to parse the date using datetime.date.fromisoformat() is
        # the fastest way to find out if it's a legal date. Its error message
        # is fine to use, but the parameter name and value are prepended.
        message = f', {exception.args[0]}' if len(exception.args) else ''
        raise ValueError(f"parameter {param_name}: value {param_value} doesn't parse as a date{message}") from None
    lower_bound_date = date.fromisoformat(lower_bound)
    upper_bound_date = date.fromisoformat(upper_bound)
    # datetime.date objects support comparisons so the values are converted to
    # date objects and a two-sided comparison is used.
    if not (lower_bound_date <= param_date_obj <= upper_bound_date):
        raise ValueError(f'parameter {param_name}: supplied date value {param_value} does not fall within '
                         f'[{lower_bound}, {upper_bound}]')
    return param_value


def _validate_int(param_name, param_value, lower_bound=-math.inf, upper_bound=math.inf):
    # Parses a param value to an int, and tests if it falls within lower
    # and upper bounds. If it succeeds, the int is returned. If it fails, a
    # ValueError is raised.

    # If it's already an int, just return it.
    if isinstance(param_value, int) or param_value is None:
        return param_value
    try:
        param_int_value = int(param_value)
    except ValueError:
        # A different ValueError is raised with a more explicit error message
        # that makes the 400 Bad Request output informative.
        raise ValueError(f"parameter {param_name}: value {param_value} doesn't parse as an integer")
    if not (lower_bound <= param_int_value <= upper_bound):
        # Checking against the bounds. By default these are (-inf, +int), which
        # are impossible to fall outside of.
        raise ValueError(f"parameter {param_name}: supplied integer value '{param_int_value}' does not fall "
                         f'between [{lower_bound}, {upper_bound}]')
    return param_int_value


def _validate_str(param_name, param_value, lower_bound=1, upper_bound=64):
    # Tests if a param value string's length falls between lower and upper
    # bounds. If it succeeds, the string is returned. If it fails, a
    # ValueError is raised.

    if param_value is None:
        return param_value
    elif not (lower_bound <= len(param_value) <= upper_bound):
        # If the reason for failure is the str is length zero, a more specific
        # error message is used.
        if len(param_value) == 0:
            raise ValueError(f'parameter {param_name}: may not be zero-length')
        # If the upper and lower bounds are equal, that's a requirement the
        # string be that length, so the error message states that.
        elif lower_bound == upper_bound:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{param_value}' is not "
                             f'equal to {lower_bound}')
        # Otherwise use the full error message.
        else:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{param_value}' does "
                             f'not fall between [{lower_bound}, {upper_bound}]')
    return param_value


def _validate_bool(param_name, param_value):
    # Parses a param value to a boolean. If it succeeds, the boolean is
    # returned. If it fails, a ValueError is raised.

    # If it's already a boolean, just return it.
    if isinstance(param_value, bool) or param_value is None:
        return param_value
    elif param_value.lower() in ('true', 't', 'yes', '1'):  # Tries to accept a
        return True                                         # variety of
    elif param_value.lower() in ('false', 'f', 'no', '0'):  # conventions for
        return False                                        # True or False.
    else:
        raise ValueError(f"parameter {param_name}: the supplied parameter value '{param_value}' does not parse as "
                         'either True or False')


def generate_create_update_argd(model_class, request_json, **argd):
    """
    Accepts a SQLAlchemy.Model subclass and a request.json object and returns a
    dict of parameter key/value pairs, whose values have been validated, that
    can be used as an argument to create_model_obj() or update_model_obj().

    :model_class:  A SQLAlchemy.Model subclass class object, the target to build
                   constructor/update arguments for.
    :request_json: The value of request.json during the execution of a flask
                   endpoint function, containing the key-value pairs to convert
                   to constructor/update arguments.
    :**argd:       (Optional.) A single key/value pair, where the key is the
                   name of a foreign key in the relevant table, and the value
                   is the value for that key supplied to the flask endpoint
                   function as a URL argument. If the value for that column in
                   request.json, it is replaced with the value.
    :return:       A dict that can be constructor/update arguments for the
                   SQLAlchemy.Model subclass target.
    """

    # An argument to _validate_date for Book, predefined for easier reading.
    tm_date_str = (date.today() + timedelta(days=1)).isoformat()

    # This data structure associates a SQLAlchemy.Model subclass object with a
    # lambda that returns a valid constructor/update argd when called with the
    # value of requests.json. Executing the lambda passes each value through the
    # correct _validate_*() function so the argd has valid parameter values.
    classes_to_argd_lambdas = {

        Author: lambda json: {     'first_name':        _validate_str(json.get('first_name')),
                                   'last_name':         _validate_str(json.get('last_name'))},

        Book: lambda json: {       'editor_id':         _validate_int(json.get('editor_id'), 0),
                                   'series_id':         _validate_int(json.get('series_id'), 0),
                                   'title':             _validate_str(json.get('title')),
                                   'publication_date':  _validate_date(json.get('publication_date'), '1990-01-01'),
                                   'edition_number':    _validate_int(json.get('edition_number'), 1, 10),
                                   'is_in_print':       _validate_bool(json.get('is_in_print'))},

        Manuscript: lambda json: { 'editor_id':         _validate_int(json.get('editor_id'), 0),
                                   'series_id':         _validate_int(json.get('series_id'), 0),
                                   'working_title':     _validate_str(json.get('working_title')),
                                   'due_date':          _validate_date(json.get('due_date'), tm_date_str, '2024-07-01'),
                                   'advance':           _validate_int(json.get('advance'), 5000, 100000)},

        Client: lambda json: {     'salesperson_id':    _validate_int(json.get('salesperson_id'), 0),
                                   'email_address':     _validate_str(json.get('email_address')),
                                   'phone_number':      _validate_str(json.get('phone_number'), 11, 11),
                                   'business_name':     _validate_str(json.get('business_name')),
                                   'street_address':    _validate_str(json.get('street_address')),
                                   'city':              _validate_str(json.get('city')),
                                   'state_or_province': _validate_str(json.get('state_or_province'), 2, 4),
                                   'zipcode':           _validate_str(json.get('zipcode'), 9, 9),
                                   'country':           _validate_str(json.get('country'))},

        Editor: lambda json: {     'first_name':        _validate_str(json.get('first_name')),
                                   'last_name':         _validate_str(json.get('last_name')),
                                   'salary':            _validate_int(json.get('salary'), 0)},

        Salesperson: lambda json: {'first_name':        _validate_str(json.get('first_name')),
                                   'last_name':         _validate_str(json.get('last_name')),
                                   'salary':            _validate_int(json.get('salary'), 0)},

        Series: lambda json: {     'title':             _validate_str(json.get('title')),
                                   'volumes':           _validate_int(json.get('volumes'), 2)}

        }

    # The lambda that computes the argd that can be constructor or update
    # arguments for the model_class arguments is located, and called with
    # request_json so it evaluates.
    create_or_update_argd = classes_to_argd_lambdas[model_class](request_json)

    # If the id_column and its value id_value are defined, and the argd's
    # value for a key of id_column is None, then it's set to id_value. (If
    # the JSON contains a different value than the one included from the URL
    # argument, it can override.)
    if len(argd):
        (id_column_name, id_column_value), = create_or_update_argd.items()
        if create_or_update_argd.get(id_column_name) is None:
            create_or_update_argd[id_column_name] = id_column_value
    return create_or_update_argd



def handle_exception(exception):
    """
    A generalized exception handler which implements an ideal handler for
    endpoint function try/except blocks.

    :exception: The exception being handled.
    :return:    A flask.Response object. NB: May raise an exception rather
                than returning.
    """
    # If the exception is a 404 error, it's passed through unmodified. (`from
    # None` ensures it isn't modified by passing through this try/except
    # statement.)
    if isinstance(exception, werkzeug.exceptions.NotFound):
        raise exception from None

    # The validation logic that checks arguments uses ValueError to indicate an
    # invalid argument. So if it's a ValueError, that's a 400; anything else is
    # a coding error, a 500.
    status = 400 if isinstance(exception, ValueError) else 500

    # If the exception has a message, it's extracted and built into a helpful
    # text for the error;
    if len(exception.args):
        return Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
    else:
        return abort(status)



def create_table_row_function(model_class):
    """
    Returns a function that executes a endpoint function POST /{table}, using
    the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for outer table
    :return:      a function that executes POST/{table}
    """
    def _internal_create_table_row(request_json):
        try:
            # Using create_model_obj() to process request.json into a
            # model_class argument dict and instance a model_class object.
            model_class_obj = create_model_obj(model_class,
                                               generate_create_update_argd(model_class, request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return handle_exception(exception)
    return _internal_create_table_row


def delete_table_row_by_id_function(model_class):
    """
    Returns a function that executes a endpoint function for DELETE
    /{table}/{id}, using the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for the table
    :returns:     a function that executes DELETE/{table}/{id}

    The returned function:

    :model_id:    The primary key value for the row to delete.
    :return:      A flask.Response object.
    """
    def _internal_delete_table_row_by_id(model_id):
        try:
            delete_model_obj(model_id, model_class)
            return jsonify(True)
        except Exception as exception:
            return handle_exception(exception)
    return _internal_delete_table_row_by_id


def delete_table_row_by_id_and_foreign_key_function(outer_class, inner_class):
    """
    Returns a function that executes DELETE
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the supplied
    SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return:      a function that executes DELETE
                  /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The returned function:

    :outer_id:    a value for the primary key column in the outer table
    :inner_id:    a value for the primary key column in the inner table; this row
                  will be deleted
    :return:      A flask.Response object.
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class', 'inner_id_column'

    def _internal_delete_table_row_by_id_and_foreign_key(outer_id, inner_id):
        try:
            # Verifying that a row in the outer table with a primary key equal
            # to outer_id exists, else it's a 404.
            outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a foreign key
            # from the outer table, else it's a 404.
            if not any(getattr(inner_class, inner_id_column) == inner_id
                       for inner_class in inner_class.query.where(
                           getattr(inner_class, outer_id_column) == outer_id)
                       ):
                return abort(404)

            # Deleting the row in the inner table with that foreign key.
            # If inner_class is Book or Manuscript, also cleans up the
            # authors_books or authors_manuscripts table.
            delete_model_obj(inner_id, inner_class)
            return jsonify(True)
        except Exception as exception:
            return handle_exception(exception)
    return _internal_delete_table_row_by_id_and_foreign_key


def display_table_rows_by_foreign_id_function(outer_class, inner_class):
    """
    Returns a function that executes an endpoint function for GET
    /{outer_table}/{outer_id}/{inner_table}, using the supplied
    SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return:      a function that executes
                  GET /{outer_table}/{outer_id}/{inner_table}

    The returned function:

    :outer_id:    a value for the primary key column in the outer table
    :return:      A flask.Response object.
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class',

    def _internal_display_table_rows_by_foreign_id(outer_id):
        try:
            outer_class.query.get_or_404(outer_id)
            # A outer_class object for every row in the inner_class table with
            # the given outer_id.
            retval = [inner_class_obj.serialize() for inner_class_obj
                      in inner_class.query.where(getattr(inner_class, outer_id_column) == outer_id)]
            if not len(retval):
                return abort(404)
            return jsonify(retval)
        except Exception as exception:
            return handle_exception(exception)
    return _internal_display_table_rows_by_foreign_id


def display_table_rows_function(model_class):
    """
    Returns an endpoint function that executes GET /{table}, using the supplied
    SQLAlchemy.Model subclasses.

    :model_class: the Model subclass for the table
    :return:      a function that executes GET /{table}

    The returned function (takes no arguments):

    :return:      a flask.Response object
    """
    def _internal_display_table_rows():
        try:
            result = [model_class_obj.serialize() for model_class_obj in model_class.query.all()]
            return jsonify(result)
        except Exception as exception:
            return handle_exception(exception)
    return _internal_display_table_rows


def display_table_row_by_id_function(model_class):
    """
    Returns an endpoint function that executes GET /{table}/{id}, using the
    supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for the table
    :return:      a function that executes GET /{table}/{id}

    The returned function:

    :model_id:    a value for the primary key column in the table
    :return:      a flask.Response object
    """

    def _internal_display_table_row_by_id(model_id):
        try:
            model_class_obj = self.model_class.query.get_or_404(model_id)
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return self.handle_exception(exception)
    return _internal_display_table_row_by_id


def display_table_row_by_id_and_foreign_key_function(outer_class, inner_class):
    """
    Returns an endpoint function that executes GET
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the supplied
    SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return:      a function that executes GET
                  /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The returned function:

    :outer_id:    a value for the primary key column in the outer table
    :inner_id:    a value for the primary key column in the inner table; this row
                  will be deleted
    :return:      a flask.Response object
    """

    def _internal_display_table_row_by_id_and_foreign_key(outer_id, inner_id):
        try:
            self.outer_class.query.get_or_404(outer_id)
            # An inner_class object for every row in the inner_class table with
            # the given outer_id.
            inner_class_objs = list(self.inner_class.query.where(getattr(self.inner_class, self.outer_id_column)
                                                                 == outer_id))
            # Iterating across the list looking for the self.inner_class object
            # with the given inner_class_id. If it's found, it's serialized and
            # returned. Otherwise, a 404 error is raised.
            for inner_class_obj in inner_class_objs:
                if getattr(inner_class_obj, self.inner_id_column) == inner_id:
                    return jsonify(inner_class_obj.serialize())
            return abort(404)
        except Exception as exception:
            return self.handle_exception(exception)
    return _internal_display_table_row_by_id_and_foreign_key


def update_table_row_by_id_function(model_class):
    """
    Returns an endpoint function that executes PATCH /{table}/{id}, using the
    supplied SQLAlchemy.Model subclass.

    :model_class:  the Model subclass for the table
    :return:       a function that executes GET /{table}/{id}

    The returned function:

    :model_id:     a value for the primary key column in the table
    :request_json: a reference to the request.json object available within the
                   endpoint function
    :return:       a flask.Response object
    """

    def _internal_update_table_row_by_id(model_id, request_json):
        try:
            # update_model_obj is used to fetch and update the model class
            # object indicates by the model_class object and its id value
            # model_id. generate_create_update_argd() is used to build its param
            # dict argument.
            model_class_obj = update_model_obj(model_id, self.model_class,
                                               generate_create_update_argd(self.model_class, request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return self.handle_exception(exception)
    return _internal_update_table_row_by_id


def update_table_row_by_id_and_foreign_key_function(outer_class, inner_class):
    """
    Returns an endpoint function that executes PATCH
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the supplied
    SQLAlchemy.Model subclasses.

    :outer_class:  the Model subclass for the outer table
    :inner_class:  the Model subclass for the inner table
    :return:       a function that executes PATCH
                   /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The returned function:

    :outer_id:     a value for the primary key column in the outer table
    :inner_id:     a value for the primary key column in the inner table; this row
                   will be deleted
    :request_json: a reference to the request.json object available within the
                   endpoint function
    :return:       a flask.Response object
    """

    def _internal_update_table_row_by_id_and_foreign_key(outer_id, inner_id, request_json):
        try:
            # Verifying that a row in the outer table with a primary key equal
            # to outer_id exists, else it's a 404.
            self.outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a foreign key
            # from the outer table, else it's a 404.
            if not any(getattr(inner_class_obj, self.inner_id_column) == inner_id for inner_class_obj
                       in self.inner_class.query.where(getattr(self.inner_class, self.outer_id_column) == outer_id)):
                return abort(404)

            # Using update_model_obj() to fetch the inner_class object and
            # update it against request.json.
            inner_class_obj = update_model_obj(inner_id,
                                               self.inner_class,
                                               generate_create_update_argd(self.inner_class,
                                                                           request_json,
                                                                           **{self.outer_id_column: outer_id}))
            db.session.add(inner_class_obj)
            db.session.commit()
            return jsonify(inner_class_obj.serialize())
        except Exception as exception:
            return self.handle_exception(exception)
    return _internal_update_table_row_by_id_and_foreign_key
