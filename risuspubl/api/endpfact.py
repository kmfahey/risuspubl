#!/usr/bin/python3

from datetime import date, timedelta

import werkzeug.exceptions

from flask import Response, abort, jsonify

from risuspubl.api.commons import create_model_obj, delete_model_obj, update_model_obj
from risuspubl.dbmodels import Author, Book, Client, Editor, Manuscript, Salesperson, Series, db


class create_or_update_model_obj_argd_factory(object):
    """
    This class serves as a source for the complex dict argument to
    create_model_obj or update_model_obj.
    """
    __slots__ = 'model_class', 'argd_prototype', 'model_id_column'

    def __init__(self, model_class, model_id_column=None):
        """
        This constructor initializes the object, and selects the
        """
        self.model_class = model_class
        self.model_id_column = model_id_column

    # These are the argds needed to execute create_model_obj or update_model_obj. They're stored in functions so that
    # request_json doesn't evaluate until they're called with a reference to the value that response.json has during the
    # execution of an endpoint function.
    def author_argd(self, request_json):
        return {'first_name':        [str,  (),         request_json.get('first_name')],
                'last_name':         [str,  (),         request_json.get('last_name')]}

    def book_argd(self, request_json):
        return {'editor_id':         [int,  (0,),       request_json.get('editor_id')],
                'series_id':         [int,  (0,),       request_json.get('series_id')],
                'title':             [str,  (),         request_json.get('title')],
                'publication_date':  [str,  (),         request_json.get('publication_date')],
                'edition_number':    [int,  (1, 10),    request_json.get('edition_number')],
                'is_in_print':       [bool, (),         request_json.get('is_in_print')]}

    def manuscript_argd(self, request_json):
        return {'editor_id':         [int,  (0,),       request_json.get('editor_id')],
                'series_id':         [int,  (0,),       request_json.get('series_id')],
                'working_title':     [str,  (),         request_json.get('working_title')],
                'due_date':          [date, ((date.today() + timedelta(days=1)).isoformat(), '2024-07-01'),
                                                        request_json.get('due_date')],
                'advance':           [int,  (5e3, 1e5), request_json.get('advance')]}

    def client_argd(self, request_json):
        return {'salesperson_id':    [int,  (0,),       request_json.get('salesperson_id')],
                'email_address':     [str,  (),         request_json.get('email_address')],
                'phone_number':      [str,  (11, 11),   request_json.get('phone_number')],
                'business_name':     [str,  (),         request_json.get('business_name')],
                'street_address':    [str,  (),         request_json.get('street_address')],
                'city':              [str,  (),         request_json.get('city')],
                'state_or_province': [str,  (2, 4),     request_json.get('state_or_province')],
                'zipcode':           [str,  (9, 9),     request_json.get('zipcode')],
                'country':           [str,  (),         request_json.get('country')]}

    def editor_argd(self, request_json):
        return {'first_name':        [str,  (),         request_json.get('first_name')],
                'last_name':         [str,  (),         request_json.get('last_name')],
                'salary':            [int,  (),         request_json.get('salary')]}

    def salesperson_argd(self, request_json):
        return {'first_name':        [str,  (),         request_json.get('first_name')],
                'last_name':         [str,  (),         request_json.get('last_name')],
                'salary':            [int,  (),         request_json.get('salary')]}

    def series_argd(self, request_json):
        return {'title':             [str,  (),         request_json.get('title')],
                'volumes':           [int,  (2, 5),     request_json.get('volumes')]}

    def generate_argd(self, request_json, id_value=None):
        classes_to_argds = {Author: self.author_argd, Book: self.book_argd,
                            Manuscript: self.manuscript_argd, Client: self.client_argd,
                            Editor: self.editor_argd, Salesperson: self.salesperson_argd,
                            Series: self.series_argd}
        # The method with the correct argd is located, and called with
        # request_json so it evaluates.
        argd = classes_to_argds[self.model_class](request_json)

        # If the id_column and its value id_value are defined, then it's set
        # under the matching parameter name if its value is None. (This way if
        # the JSON argument contains a different value than the one included
        # from the URL argument, it can override.)
        if self.id_column is not None and id_value is not None:
            for param_name, param_list in argd.items():
                if param_name != self.id_column:
                    continue
                if param_list[2] is None:
                    param_list[2] = id_value
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
            argd_factory = create_or_update_model_obj_argd_factory(self.model_class)
            # Using create_model_obj() to process request.json into a model_class
            # argument dict and instance a model_class object.
            model_class_obj = create_model_obj(self.model_class,
                                               argd_factory.generate_argd(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            status = 400 if isinstance(exception, ValueError) else 500

            # If the exception has a message, it's extracted and built into a helpful text for the error;
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            status = 500
            # If the exception has a message, it's extracted and built into a helpful text for the error;
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            if isinstance(exception, werkzeug.exceptions.NotFound):
                raise exception from None

            # If the exception has a message, it's extracted and built into a helpful text for the error;
            status = 400 if isinstance(exception, ValueError) else 500
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)

                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            status = 500
            # If the exception has a message, it's extracted and built into a helpful text for the error;
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            if isinstance(exception, werkzeug.exceptions.NotFound):
                raise exception from None

            status = 500
            # If the exception has a message, it's extracted and built into a helpful text for the error;
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            # Iterating across the list looking for the self.inner_class object with
            # the given inner_class_id. If it's found, it's serialized and
            # returned. Otherwise, a 404 error is raised.
            for inner_class_obj in inner_class_objs:
                if getattr(inner_class_obj, self.inner_id_column) == inner_id:
                    return jsonify(inner_class_obj.serialize())
            return abort(404)
        except Exception as exception:
            # The validation logic that checks arguments uses ValueError to
            # indicate an invalid argument. So if it's a ValueError, that's a 400;
            # anything else is a coding error, a 500.
            if isinstance(exception, werkzeug.exceptions.NotFound):
                raise exception from None

            status = 500
            # If the exception has a message, it's extracted and built into a helpful text for the error;
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            argd_factory = create_or_update_model_obj_argd_factory(self.model_class)
            # update_model_obj is used to fetch and update the model class
            # object indicates by the model_class object and its id value
            # model_id. create_or_update_model_obj_argd_factory.generate_argd()
            # is used to build its param dict argument.
            model_class_obj = update_model_obj(model_id, self.model_class,
                                               argd_factory.generate_argd(request_json))
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            # If the exception has a message, it's extracted and built into a helpful text for the error;
            status = 500
            return (Response(f'{exception.__class__.__name__}: {exception.args[0]}', status=status)
                    # otherwise a messageless error is raised.
                    if len(exception.args) else abort(status))


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
            argd_factory = create_or_update_model_obj_argd_factory(self.inner_class, self.outer_id_column)
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
                                               argd_factory.generate_argd(request_json, outer_id))
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
