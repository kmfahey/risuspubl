#!/usr/bin/python3

import math
from datetime import date, timedelta

from flask import Response, abort, jsonify

import werkzeug.exceptions

from risuspubl.dbmodels import Author, Authors_Books, Authors_Manuscripts, Book, Client, Editor, Manuscript, \
        SalesRecord, Salesperson, Series, db


# This lookup table associates a *_id param name with the SQLAlchemy.Model
# subclass class object representing the table where a column by that name is
# the primary key. Used to validate whether a parameter with such a name has a
# value that is associated with a row in that table.
_id_params_to_model_subclasses = {'book_id': Book, 'client_id': Client, 'editor_id': Editor, 
                                  'manuscript_id': Manuscript, 'sales_record_id': SalesRecord, 
                                  'salesperson_id': Salesperson, 'series_id': Series}


def _handle_exception(exception):
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
    return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
            # otherwise a messageless error is raised.
            if len(exception.args) else abort(status))


def create_model_obj(model_subclass, params_argd, optional_params=set()):
    """
    This function builds an SQLAlchemy.Model subclass object. It uses the Model
    subclass class object and the dict of parameter names, values, and validator
    instructions to build a dict of arguments to the Model subclass constructor,
    instantiates an object and returns it.

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
            # This step matches a *_id parameters with the Model class for the
            # table where that column is a primary key, and does a get() to
            # confirm the *_id value corresponds to a row in that table. If not,
            # a ValueError is raised.
            id_model_subclass = _id_params_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        model_obj_args[param_name] = param_value
    return model_subclass(**model_obj_args)


def update_model_obj(id_val, model_subclass, params_argd):
    """
    This function updates a SQLAlchemy.Model subclass object. It uses the id
    value and Model subclass class object to look up a model object, and then
    uses the dict of parameter names, values, and validator instructions to
    update the column values on that object. Then the object is returned.

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
            # This step matches a *_id parameters with the Model class for the
            # table where that column is a primary key, and does a get() to
            # confirm the *_id value corresponds to a row in that table. If not,
            # a ValueError is raised.
            id_model_subclass = _id_params_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        setattr(model_obj, param_name, param_value)
    return model_obj


def delete_model_obj(id_val, model_subclass):
    """
    This function looks up an id value in the provided SQLAlchemy.Model
    subclass, and has that row in that table deleted. If the model subclass
    is Book or Manuscript, the matching row(s) in authors_books or
    authors_manuscripts are deleted too.

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


class create_or_update_argd_gen(object):
    """
    This class serves as a source for the complex dict argument to
    create_model_obj or update_model_obj.
    """
    __slots__ = 'model_class', 'argd_prototype', 'model_id_column'

    def __init__(self, model_class, model_id_column=None):
        """
        This constructor initializes the object.
        """
        self.model_class = model_class
        self.model_id_column = model_id_column

    def validate_date(self, param_name, param_value, lower_bound='1900-01-01', upper_bound=date.today().isoformat()):
        """
        This method parses a param value to a date, and tests if it falls within
        lower and upper bounds. If it succeeds, the param value string is
        returned. If it fails, a ValueError is raised.

        :param_name:  The name of the JSON parameter. Used in the ValueError
                      exception message if one is raised.
        :param_value: The value of the JSON parameter, a string.
        :lower_bound: The lower bound that the float value is tested against;
                      must be greater than or equal to. Defaults to 1900-01-01.
        :upper_bound: The upper bound that the float value is tested against;
                      must be less than or equal to. Defaults to today's date,
                      in YYYY-MM-DD format.
        :return:      A string, the original param value.
        """
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

    def validate_int(self, param_name, param_value, lower_bound=-math.inf, upper_bound=math.inf):
        """
        This method parses a param value to an int, and tests if it falls within
        lower and upper bounds. If it succeeds, the int is returned. If it
        fails, a ValueError is raised.

        :param_name:  The name of the JSON parameter. Used in the ValueError
                      exception message if one is raised.
        :param_value: The value of the JSON parameter, a string.
        :lower_bound: The lower bound that the int value is tested against;
                      must be greater than or equal to. Defaults to -Infinity.
        :upper_bound: The upper bound that the int value is tested against;
                      must be less than or equal to. Defaults to +Infinity.
        :return:      An int, parsed from the param value.
        """
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

    def validate_str(self, param_name, param_value, lower_bound=1, upper_bound=64):
        """
        This method tests if a param value string's length falls between lower
        and upper bounds. If it succeeds, the string is returned. If it fails, a
        ValueError is raised.

        :param_name:  The name of the JSON parameter. Used in the ValueError
                      exception message if one is raised.
        :param_value: The value of the JSON parameter, a string.
        :lower_bound: The lower bound on the value's length, default 1.
        :upper_bound: The upper bound on the value's length, default 64.
        :return:      A string, the param_value unmodified.
        """
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

    def validate_bool(self, param_name, param_value):
        """
        This method parses a param value to a boolean. If it succeeds, the
        boolean is returned. If it fails, a ValueError is raised.

        :param_name:  The name of the JSON parameter. Used in the ValueError
                      exception message if one is raised.
        :param_value: The value of the JSON parameter, a string.
        :return:      A boolean, parsed from the param_value.
        """
        # If it's already a boolean, just return it.
        if isinstance(param_value, bool) or param_value is None:
            return param_value                                  # Tries to accept a
        elif param_value.lower() in ('true', 't', 'yes', '1'):  # variety of
            return True                                         # conventions for a
        elif param_value.lower() in ('false', 'f', 'no', '0'):  # True boolean or a
            return False                                        # False boolean.
        else:
            raise ValueError(f"parameter {param_name}: the supplied parameter value '{param_value}' does not parse as "
                             'either True or False')

    # These are the argds needed to execute create_model_obj or
    # update_model_obj. They're stored in functions so that request_json
    # doesn't evaluate until they're called with a reference to the value that
    # response.json has during the execution of an endpoint function.
    def _argd_for_author_obj(self, request_json):
        return {'first_name':        self.validate_str(request_json.get('first_name')),
                'last_name':         self.validate_str(request_json.get('last_name'))}

    def _argd_for_book_obj(self, request_json):
        return {'editor_id':         self.validate_int(request_json.get('editor_id'), 0),
                'series_id':         self.validate_int(request_json.get('series_id'), 0),
                'title':             self.validate_str(request_json.get('title')),
                'publication_date':  self.validate_str(request_json.get('publication_date')),
                'edition_number':    self.validate_int(request_json.get('edition_number'), 1, 10),
                'is_in_print':       self.validate_bool(request_json.get('is_in_print'))}

    def _argd_for_manuscript_obj(self, request_json):
        return {'editor_id':         self.validate_int(request_json.get('editor_id'), 0),
                'series_id':         self.validate_int(request_json.get('series_id'), 0),
                'working_title':     self.validate_str(request_json.get('working_title')),
                'due_date':          self.validate_date(request_json.get('due_date'),
                                                   (date.today() + timedelta(days=1)).isoformat(), '2024-07-01'),
                'advance':           self.validate_int(request_json.get('advance'), 5000, 100000)}

    def _argd_for_client_obj(self, request_json):
        return {'salesperson_id':    self.validate_int(request_json.get('salesperson_id'), 0),
                'email_address':     self.validate_str(request_json.get('email_address')),
                'phone_number':      self.validate_str(request_json.get('phone_number'), 11, 11),
                'business_name':     self.validate_str(request_json.get('business_name')),
                'street_address':    self.validate_str(request_json.get('street_address')),
                'city':              self.validate_str(request_json.get('city')),
                'state_or_province': self.validate_str(request_json.get('state_or_province'), 2, 4),
                'zipcode':           self.validate_str(request_json.get('zipcode'), 9, 9),
                'country':           self.validate_str(request_json.get('country'))}

    def _argd_for_editor_obj(self, request_json):
        return {'first_name':        self.validate_str(request_json.get('first_name')),
                'last_name':         self.validate_str(request_json.get('last_name')),
                'salary':            self.validate_int(request_json.get('salary'))}

    def _argd_for_salesperson_obj(self, request_json):
        return {'first_name':        self.validate_str(request_json.get('first_name')),
                'last_name':         self.validate_str(request_json.get('last_name')),
                'salary':            self.validate_int(request_json.get('salary'))}

    def _argd_for_series_obj(self, request_json):
        return {'title':             self.validate_str(request_json.get('title')),
                'volumes':           self.validate_int(request_json.get('volumes'), 2, 5)}

    def generate_argd(self, request_json, id_value=None):
        class_to_argd_method = {Author:      self._argd_for_author_obj,
                                Book:        self._argd_for_book_obj,
                                Manuscript:  self._argd_for_manuscript_obj,
                                Client:      self._argd_for_client_obj,
                                Editor:      self._argd_for_editor_obj,
                                Salesperson: self._argd_for_salesperson_obj,
                                Series:      self._argd_for_series_obj}
        # The method with the correct argd is located, and called with
        # request_json so it evaluates.
        argd = class_to_argd_method[self.model_class](request_json)

        # If the id_column and its value id_value are defined, and the argd's
        # value for a key of id_column is None, then it's set to id_value. (If
        # the JSON contains a different value than the one included from the URL
        # argument, it can override.)
        if self.id_column is not None and id_value is not None:
            if argd.get(self.id_column) is None:
                argd[self.id_column] = id_value
        return argd


class create_class_obj_factory(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function POST /{table}. Its constructor accepts this argument:

    :model_class:  the Model subclass for outer table

    Its __call__ method accepts this argument:

    :request_json: a reference to the request.json object available within the
                   endpoint function
    """
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class):
        self.model_class = model_class

    def __call__(self, request_json):
        try:
            argd_factory = create_or_update_argd_gen(self.model_class)
            # Using create_model_obj() to process request.json into a
            # model_class argument dict and instance a model_class object.
            model_class_obj = create_model_obj(self.model_class,
                                               argd_factory.generate_argd(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return _handle_exception(exception)


class delete_class_obj_by_id_factory(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function DELETE /{table}/{id}. Its constructor accepts this argument:

    :model_class:     the Model subclass for the table
    :model_id_column: the name of the primary key column in the table

    Its __call__ method accepts these arguments:

    :model_id:        a value for the primary key column in the table
    """
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class, model_id_column):
        self.model_class = model_class
        self.model_id_column = model_id_column

    def __call__(self, model_id):
        try:
            delete_model_obj(model_id, self.model_class)
            return jsonify(True)
        except Exception as exception:
            return _handle_exception(exception)


class delete_one_classes_other_class_obj_by_id_factory(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function DELETE /{outer_table}/{outer_id}/{inner_table}/{inner_id}. Its
    constructor accepts these arguments:

    :outer_class:     the Model subclass for the outer table
    :outer_id_column: the name of the primary key column in the outer table
    :inner_class:     the Model subclass for the inner table
    :inner_id_column: the name of the primary key column in the inner table

    Its __call__ method accepts these arguments:

    :outer_id:        a value for the primary key column in the outer table
    :inner_id:        a value for the primary key column in the inner table; this row
                      will be deleted
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class', 'inner_id_column'

    def __init__(self, outer_class, outer_id_column, inner_class, inner_id_column):
        self.outer_class = outer_class
        self.outer_id_column = outer_id_column
        self.inner_class = inner_class
        self.inner_id_column = inner_id_column

    def __call__(self, outer_id, inner_id):
        try:
            # Verifying that a row in the outer table with a primary key equal
            # to outer_id exists, else it's a 404.
            self.outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a foreign key
            # from the outer table, else it's a 404.
            if not any(getattr(inner_class, self.inner_id_column) == inner_id
                       for inner_class in self.inner_class.query.where(
                           getattr(self.inner_class, self.outer_id_column) == outer_id)
                       ):
                return abort(404)

            # Deleting the row in the inner table with that foreign key.
            # If inner_class is Book or Manuscript, also cleans up the
            # authors_books or authors_manuscripts table.
            delete_model_obj(inner_id, self.inner_class)
            return jsonify(True)
        except Exception as exception:
            return _handle_exception(exception)


class show_all_of_one_classes_other_class_objs(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function GET /{outer_table}/{outer_id}/{inner_table}. Its constructor
    accepts these arguments:

    :outer_class:     the Model subclass for the outer table
    :outer_id_column: the name of the primary key column in the outer table
    :inner_class:     the Model subclass for the inner table

    Its __call__ method accepts this argument:

    :outer_id:        a value for the primary key column in the outer table
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class',

    def __init__(self, outer_class, outer_id_column, inner_class):
        self.outer_class = outer_class
        self.outer_id_column = outer_id_column
        self.inner_class = inner_class

    def __call__(self, outer_id):
        try:
            self.outer_class.query.get_or_404(outer_id)
            # A outer_class object for every row in the inner_class table with
            # the given outer_id.
            retval = [inner_class_obj.serialize() for inner_class_obj
                      in self.inner_class.query.where(getattr(self.inner_class, self.outer_id_column) == outer_id)]
            if not len(retval):
                return abort(404)
            return jsonify(retval)
        except Exception as exception:
            return _handle_exception(exception)


class show_class_index(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function GET /{table}. Its constructor accepts this argument:

    :model_class:     the Model subclass for the outer table

    Its __call__ method takes no arguments.
    """
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class):
        self.model_class = model_class

    def __call__(self):
        try:
            result = [model_class_obj.serialize() for model_class_obj in self.model_class.query.all()]
            return jsonify(result)
        except Exception as exception:
            return _handle_exception(exception)


class show_class_obj_by_id(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function GET /{table}/{id}. Its constructor
    accepts this argument:

    :model_class: the Model subclass for the table

    Its __call__ method accepts this argument:

    :model_id:    a value for the primary key column in the table
    """
    __slots__ = 'model_class',

    def __init__(self, model_class):
        self.model_class = model_class

    def __call__(self, model_id):
        try:
            model_class_obj = self.model_class.query.get_or_404(model_id)
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return _handle_exception(exception)


class show_one_classes_other_class_obj_by_id(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function GET /{outer_table}/{outer_id}/{inner_table}/{inner_id}. Its
    constructor accepts these arguments:

    :outer_class:     the Model subclass for the outer table
    :outer_id_column: the name of the primary key column in the outer table
    :inner_class:     the Model subclass for the inner table
    :inner_id_column: the name of the primary key column in the inner table

    Its __call__ method accepts these arguments:

    :outer_id:        a value for the primary key column in the outer table
    :inner_id:        a value for the primary key column in the inner table; this row
                      will be deleted
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class', 'inner_id_column'

    def __init__(self, outer_class, outer_id_column, inner_class, inner_id_column):
        self.outer_class = outer_class
        self.outer_id_column = outer_id_column
        self.inner_class = inner_class
        self.inner_id_column = inner_id_column

    def __call__(self, outer_id, inner_id):
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
            return _handle_exception(exception)


class update_class_obj_by_id_factory(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function PATCH /{table}/{id}. Its constructor accepts these arguments:

    :model_class:     the Model subclass for the outer table
    :model_id_column: the name of the primary key column in the outer table

    Its __call__ method accepts these arguments:

    :model_id:        a value for the primary key column in the outer table
    :request_json:    a reference to the request.json object available within the
                      endpoint function
    """
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class, model_id_column):
        self.model_class = model_class
        self.model_id_column = model_id_column

    def __call__(self, model_id, request_json):
        try:
            argd_factory = create_or_update_argd_gen(self.model_class)
            # update_model_obj is used to fetch and update the model class
            # object indicates by the model_class object and its id value
            # model_id. create_or_update_argd_gen.generate_argd()
            # is used to build its param dict argument.
            model_class_obj = update_model_obj(model_id, self.model_class,
                                               argd_factory.generate_argd(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return _handle_exception(exception)


class update_one_classes_other_class_obj_by_id_factory(object):
    """
    This class implements a callable object that executes an abstracted endpoint
    function PATCH /{outer_table}/{outer_id}/{inner_table}/{inner_id}. Its
    constructor accepts these arguments:

    :outer_class:     the Model subclass for the outer table
    :outer_id_column: the name of the primary key column in the outer table
    :inner_class:     the Model subclass for the inner table
    :inner_id_column: the name of the primary key column in the inner table

    Its __call__ method accepts these arguments:

    :outer_id:        a value for the primary key column in the outer table
    :inner_id:        a value for the primary key column in the inner table; this row
                      will be deleted
    :request_json:    a reference to the request.json object available within the
                      endpoint function
    """
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class', 'inner_id_column', 'argd'

    def __init__(self, outer_class, outer_id_column, inner_class, inner_id_column):
        self.outer_class = outer_class
        self.outer_id_column = outer_id_column
        self.inner_class = inner_class
        self.inner_id_column = inner_id_column

    def __call__(self, outer_id, inner_id, request_json):
        try:
            argd_factory = create_or_update_argd_gen(self.inner_class, self.outer_id_column)
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
            inner_class_obj = update_model_obj(inner_id, self.inner_class,
                                               argd_factory.generate_argd(request_json, outer_id))
            db.session.add(inner_class_obj)
            db.session.commit()
            return jsonify(inner_class_obj.serialize())
        except Exception as exception:
            return _handle_exception(exception)
