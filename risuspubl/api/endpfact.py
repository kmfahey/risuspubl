#!/usr/bin/python3

import abc
import math
from datetime import date, timedelta

from flask import Response, abort, jsonify

from risuspubl.dbmodels import Author, Authors_Books, Authors_Manuscripts, Book, Client, Editor, Manuscript, SalesRecord, \
        Salesperson, Series, db
from risuspubl.api.commons import create_model_obj, update_model_obj, delete_model_obj

import werkzeug.exceptions


class create_or_update_param_tab_factory(object):
    __slots__ = 'model_class', 'param_tab_prototype', 'model_id_column'

    param_tab_prototypes = {
        Author:      {'first_name':        (str,  ()),
                      'last_name':         (str,  ())},

        Book:        {'editor_id':         (int,  (0,)),
                      'series_id':         (int,  (0,)),
                      'title':             (str,  ()),
                      'publication_date':  (str,  ()),
                      'edition_number':    (int,  (1, 10)),
                      'is_in_print':       (bool, ())},

        Manuscript:  {'editor_id':         (int,  (0,)),
                      'series_id':         (int,  (0,)),
                      'working_title':     (str,  ()),
                      'due_date':          (date, ((date.today() + timedelta(days=1)).isoformat(), "2024-07-01")),
                      'advance':           (int,  (5000, 100000))},

        Client:      {'salesperson_id':    (int,  (0,)),
                      'email_address':     (str,  ()),
                      'phone_number':      (str,  (11, 11)),
                      'business_name':     (str,  ()),
                      'street_address':    (str,  ()),
                      'city':              (str,  ()),
                      'state_or_province': (str,  (2, 4)),
                      'zipcode':           (str,  (9, 9)),
                      'country':           (str,  ())},

        Editor:      {'first_name':        (str,  ()),
                      'last_name':         (str,  ()),
                      'salary':            (int,  ())},

        Salesperson: {'first_name':        (str,  ()),
                      'last_name':         (str,  ()),
                      'salary':            (int,  ())},

        Series:      {'title':             (str,  ()),
                      'volumes':           (int,  (2, 5))}
        }

    def __init__(self, model_class, model_id_column=None):
        self.model_class = model_class
        self.model_id_column = model_id_column
        self.param_tab_prototype = self.param_tab_prototypes[model_class].copy()

    def generate_param_tab(self, request_json, id_value=None):
        param_tab = dict()
        for param_name, type_validargs_tuple in self.param_tab_prototype.items():
            if param_name == self.model_id_column:
                param_tab[param_name] = type_validargs_tuple + (id_value,)
            else:
                param_tab[param_name] = type_validargs_tuple + (request_json.get(param_name),)
        return param_tab


class endpoint_factory(abc.ABC):

    __abstractmethods__ = frozenset({'__init__', '__call__'})

    # This lookup table associates a type object to the validator static method
    # for that data type. This dict is populated during the class definition
    # using the register_validator decorator.
    types_to_validators = {}

    # This lookup table associates a *_id param name with the SQLAlchemy.Model
    # subclass class object representing the table where a column by that name
    # is the primary key. Used to validate whether a parameter with such a name
    # has a value that is associated with a row in that table.
    id_params_to_model_subclasses = {'book_id': Book, 'client_id': Client, 'editor_id': Editor,
                                     'manuscript_id': Manuscript, 'sales_record_id': SalesRecord,
                                     'salesperson_id': Salesperson, 'series_id': Series}


class delete_one_classes_other_class_obj_by_id_factory(endpoint_factory):
    """
    This class implements via its __call_ method an abstracted endpoint function
    DELETE /{outer_table}/{outer_id}/{inner_table}/{inner_id}. Its constructor
    accepts these arguments:

    :outer_class:     the Model subclass for the outer table
    :outer_id_column: the name of the primary key column in the outer table
    :inner_class:     the Model subclass for the inner table
    :inner_id_column: the name of the primary key column in the inner table

    Its __call__ method accepts these arguments:

    :outer_id:        a value for the primary key column in the outer table
    :inner_id:        a value for the primary key column in the inner table; this row
                      will be deleted

    The __call__ method, intended to power a flask.blueprint()ed function,
    verifies that a row exists in the outer table by the outer_id argument,
    and verifies that a row exists in the inner table with its primary key
    column set to the inner_id value and its column with the same name as the
    outer table's id column set to the outer_id value. This second row is then
    deleted.

    If the inner_table is books or manuscripts, then inner_id_column is
    either book_id or manuscript_id, and the rows in authors_books or
    authors_manuscripts with the given book_id or manuscript_id are also
    deleted.
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

            # Deleting the row in the inner table with that foreign key. If
            # inner_class is Book or Manuscript, also cleans up the authors_books
            # or authors_manuscripts table.
            delete_model_obj(inner_id, self.inner_class)
            return jsonify(True)
        except Exception as exception:
            # If the exception is a 404 error, it's passed through unmodified.
            # (`from None` ensures it isn't modified by passing throug this
            # try/except statement.)
            if isinstance(exception, werkzeug.exceptions.NotFound):
                raise exception from None

            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            status = 400 if isinstance(exception, ValueError) else 500

            # If the exception has a message, it's extracted and built into a helpful text for the error; 
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


class update_one_classes_other_class_obj_by_id_factory(endpoint_factory):
    __slots__ = 'outer_class', 'outer_id_column', 'inner_class', 'inner_id_column', 'param_tab'

    def __init__(self, outer_class, outer_id_column, inner_class, inner_id_column):
        self.outer_class = outer_class
        self.outer_id_column = outer_id_column
        self.inner_class = inner_class
        self.inner_id_column = inner_id_column
        self.param_tab_factory = create_or_update_param_tab_factory(inner_class, outer_id_column)

    def __call__(self, outer_id, inner_id, request_json):
        try:
            # Verifying that a row in the outer table with a primary key equal
            # to outer_id exists, else it's a 404.
            self.outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a foreign key
            # from the outer table, else it's a 404.
            if not any(getattr(inner_class_obj, self.inner_id_column) == inner_id for inner_class_obj
                       in self.inner_class.query.where(getattr(self.inner_class, self.outer_id_column) == outer_id)):
                return abort(404)

            # Using update_model_obj() to fetch the inner_class object and update it
            # against request.json.
            inner_class_obj = update_model_obj(inner_id, self.inner_class,
                                               self.param_tab_factory.generate_param_tab(request_json, outer_id))
            db.session.add(inner_class_obj)
            db.session.commit()
            return jsonify(inner_class_obj.serialize())
        except Exception as exception:
            # If the exception is a 404 error, it's passed through unmodified.
            # (`from None` ensures it isn't modified by passing throug this
            # try/except statement.)
            if isinstance(exception, werkzeug.exceptions.NotFound):
                raise exception from None

            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            status = 400 if isinstance(exception, ValueError) else 500

            # If the exception has a message, it's extracted and built into a helpful text for the error; 
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


class delete_class_obj_by_id_factory(endpoint_factory):
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class, model_id_column):
        self.model_class = model_class
        self.model_id_column = model_id_column

    def __call__(self, model_id):
        try:
            delete_model_obj(model_id, self.model_class)
            return jsonify(True)
        except Exception as exception:
            # If the exception has a message, it's extracted and built into a helpful text for the error; 
            return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=500)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


class update_class_obj_by_id_factory(endpoint_factory):
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class, model_id_column):
        self.model_class = model_class
        self.model_id_column = model_id_column
        self.param_tab_factory = create_or_update_param_tab_factory(model_class)

    def __call__(self, model_id, request_json):
        try:
            # update_model_obj is used to fetch and update the model class
            # object indicates by the model_class object and its id value
            # model_id. create_or_update_param_tab_factory.generate_param_tab()
            # is used to build its param dict argument.
            model_class_obj = update_model_obj(model_id, self.model_class,
                                               self.param_tab_factory.generate_param_tab(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            # If the exception has a message, it's extracted and built into a helpful text for the error; 
            return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=500)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


class create_class_obj_factory(endpoint_factory):
    __slots__ = 'model_class', 'model_id_column'

    def __init__(self, model_class):
        self.model_class = model_class
        self.param_tab_factory = create_or_update_param_tab_factory(model_class)

    def __call__(self, request_json):
        try:
            # Using create_model_obj() to process request.json into a model_class
            # argument dict and instance a model_class object.
            model_class_obj = create_model_obj(self.model_class,
                                               self.param_tab_factory.generate_param_tab(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            status = 400 if isinstance(exception, ValueError) else 500

            # If the exception has a message, it's extracted and built into a helpful text for the error; 
            return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))
