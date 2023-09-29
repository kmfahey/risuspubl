#!/usr/bin/python3

import math
import traceback
from datetime import date, timedelta
from operator import attrgetter

from flask import Response, abort, jsonify

from risuspubl.dbmodels import (
    Author,
    AuthorMetadata,
    AuthorsBooks,
    AuthorsManuscripts,
    Book,
    Client,
    Editor,
    Manuscript,
    SalesRecord,
    Salesperson,
    Series,
    db,
)

import werkzeug.exceptions


# Associates a *_id param name with the SQLAlchemy.Model subclass class
# object representing the table where a column by that name is the
# primary key. Used to validate whether a parameter with such a name has
# a value that is associated with a row in that table.
_foreign_keys_to_model_subclasses = {
    "author_id": Author,
    "book_id": Book,
    "client_id": Client,
    "editor_id": Editor,
    "manuscript_id": Manuscript,
    "sales_record_id": SalesRecord,
    "salesperson_id": Salesperson,
    "series_id": Series,
}


def crt_model_obj(model_subclass, params_argd, optional_params=()):
    """
    Instantiates an object in the provided SQLAlchemy.Model subclass
    using the dict of key/value pairs as arguments to the constructor.
    A value in that dict can be None if the key is in optional_params,
    otherwise a ValueError is raised. The object is returned.

    :model_subclass: An SQLAlchemy.Model subclass class object, the
    class to instance an object of.
    :params_argd: A dict mapping of parameter keys to values.
    :optional_params: An optional argument, a set of parameter names
    that are not required for the constructor. If the value of one of
    these parameters is None, it's skipped. If a parameter does NOT
    occur in this set, and it's None, a ValueError is raised.
    :return: An instance of the class that was the first argument.
    """
    model_obj_args = dict()
    for param_name, param_value in params_argd.items():
        # optional_params is the list of names of parameters that may be
        # None.
        if param_value is None and param_name in optional_params:
            continue
        # If a required param is none, a ValueError is raised.
        elif param_value is None:
            raise ValueError(f"required parameter '{param_name}' not present")
        if param_name.endswith("_id") and param_value is not None:
            # Matching a *_id parameter with the Model class for the
            # table where that column is a primary key, and doing a
            # get() to confirm the *_id value corresponds to a row in
            # that table. If not, a ValueError is raised.
            id_model_subclass = _foreign_keys_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(
                    f"supplied '{param_name}' value '{param_value}' does not "
                    + "correspond to any row in the "
                    + f"`{id_model_subclass.__tablename__}` table"
                )
        model_obj_args[param_name] = param_value
    return model_subclass(**model_obj_args)


def updt_model_obj(id_val, model_subclass, params_argd):
    """
    Retrieves the object in the SQLAlchemy.Model subclass by the given
    id, and updates it using the dict of key/value pairs to assign new
    attribute values. If a value in the parameter argd is None, it is
    skipped. The object is *not* saved, just returned. The calling code
    has to save it itself.

    :model_subclass: An SQLAlchemy.Model subclass class object, the
    class to instance an object of.
    :params_argd: A dict of parameter keys to values.
    :return: An instance of the class that was the first argument.
    """
    model_obj = model_subclass.query.get_or_404(id_val)
    # If all the dict's param_value slots are None, this update can't
    # proceed bc there's nothing to update, so a ValueError is raised.
    if all(param_value is None for param_value in params_argd.values()):
        raise ValueError(
            "update action executed with no parameters indicating fields to update"
        )
    for param_name, param_value in params_argd.items():
        if param_value is None:
            continue
        if param_name.endswith("_id"):
            # Matching a *_id parameters with the Model class for the
            # table where that column is a primary key, and doing a
            # get() to confirm the *_id value corresponds to a row in
            # that table. If not, a ValueError is raised.
            id_model_subclass = _foreign_keys_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(
                    f"supplied '{param_name}' value '{param_value}' does not "
                    + "correspond to any row in the "
                    + f"`{id_model_subclass.__tablename__}` table"
                )
        setattr(model_obj, param_name, param_value)
    return model_obj


def del_model_obj(id_val, model_subclass):
    """
    Looks up an id value in the provided SQLAlchemy.Model subclass, and
    has the matching row in that table deleted. If the model subclass
    is Book or Manuscript, the matching row(s) in authors_books or
    authors_manuscripts are deleted too.

    :id_val: An int, the value of the id primary key column of the table
    represented by the model subclass argument.
    :model_subclass: A subclass of SQLAlchemy.Model representing the
    table to delete a row from.
    :return: None
    """
    model_obj = model_subclass.query.get_or_404(id_val)
    # In the case of Book or Manuscript objects, there's also
    # corresponding rows in authors_books or authors_manuscripts that
    # need to be deleted as well.
    if model_subclass is Book:
        ab_del = AuthorsBooks.delete().where(AuthorsBooks.columns[1] == id_val)
        db.session.execute(ab_del)
        db.session.commit()
    elif model_subclass is Manuscript:
        am_del = AuthorsManuscripts.delete().where(
            AuthorsManuscripts.columns[1] == id_val
        )
        db.session.execute(am_del)
        db.session.commit()
    db.session.delete(model_obj)
    db.session.commit()


def _validate_date(
    param_name,
    param_value,
    lower_bound="1900-01-01",
    upper_bound=date.today().isoformat(),
):
    # Parses a param value to a date, and tests if it falls within
    # lower and upper bounds. If it succeeds, the param value string is
    # returned. If it fails, a ValueError is raised.
    if param_value is None:
        return param_value
    try:
        param_date_obj = date.fromisoformat(param_value)
    except ValueError as exception:
        # Attempting to parse the date using
        # datetime.date.fromisoformat() is the fastest way to find out
        # if it's a legal date. Its error message is fine to use, but
        # the parameter name and value are prepended.
        message = f", {exception.args[0]}" if len(exception.args) else ""
        raise ValueError(
            f"parameter {param_name}: value {param_value} doesn't parse as a "
            + f"date{message}"
        ) from None
    lower_bound_date = date.fromisoformat(lower_bound)
    upper_bound_date = date.fromisoformat(upper_bound)
    # datetime.date objects support comparisons so the values are
    # dateconverted to objects and a two-sided comparison is used.
    if not (lower_bound_date <= param_date_obj <= upper_bound_date):
        raise ValueError(
            f"parameter {param_name}: supplied date value {param_value} does "
            + f"not fall within [{lower_bound}, {upper_bound}]"
        )
    return param_value


def _validate_int(param_name, param_value, lower_bound=-math.inf, upper_bound=math.inf):
    # Parses a param value to an int, and tests if it falls within lower
    # and upper bounds. If it succeeds, the int is returned. If it
    # fails, a ValueError is raised.

    # If it's already an int, just return it.
    if isinstance(param_value, int) or param_value is None:
        return param_value
    try:
        param_int_value = int(param_value)
    except ValueError:
        # A different ValueError is raised with a more explicit error
        # message that makes the 400 Bad Request output informative.
        raise ValueError(
            f"parameter {param_name}: value {param_value} doesn't parse as an integer"
        )
    if not (lower_bound <= param_int_value <= upper_bound):
        # Checking against the bounds. By default, these are (-inf,
        # +inf), a range that will include any input number apart
        # from NaN.
        if lower_bound == -math.inf and upper_bound != math.inf:
            raise ValueError(
                f"parameter {param_name}: supplied integer value "
                + f"'{param_int_value}' is greater than {upper_bound}"
            )
        elif lower_bound != -math.inf and upper_bound == math.inf:
            raise ValueError(
                f"parameter {param_name}: supplied integer value "
                + f"'{param_int_value}' is less than {lower_bound}"
            )
        else:
            raise ValueError(
                f"parameter {param_name}: supplied integer value "
                + f"'{param_int_value}' does not fall within [{lower_bound}, "
                + f"{upper_bound}]"
            )
    return param_int_value


def _validate_str(param_name, param_value, lower_bound=1, upper_bound=64.0):
    # Tests if a param value string's length falls between lower and
    # upper bounds. If it succeeds, the string is returned. If it fails,
    # a ValueError is raised.

    if param_value is None:
        return param_value
    elif not (lower_bound <= len(param_value) <= upper_bound):
        # If the reason for failure is the str is length zero, a more
        # specific error message is used.
        if len(param_value) == 0:
            raise ValueError(f"parameter {param_name}: may not be zero-length")
        elif len(param_value) < lower_bound and upper_bound == math.inf:
            raise ValueError(
                f"parameter {param_name}: the supplied string value "
                + f"'{param_value}' is not at least {lower_bound} characters long"
            )
        elif lower_bound == 0 and len(param_value) > upper_bound:
            raise ValueError(
                f"parameter {param_name}: the supplied string value "
                + f"'{param_value}' is more than {upper_bound} characters in length"
            )
        # If the upper and lower bounds are equal, that's a requirement
        # the string be that length, so the error message states that.
        elif lower_bound == upper_bound:
            raise ValueError(
                f"parameter {param_name}: the length of supplied string value "
                + f"'{param_value}' is not equal to {lower_bound}"
            )
        # Otherwise use the full error message.
        else:
            raise ValueError(
                f"parameter {param_name}: the length of supplied string value "
                + f"'{param_value}' does not fall between [{lower_bound}, "
                + f"{upper_bound}]"
            )
    return param_value


def _validate_bool(param_name, param_value):
    # Parses a param value to a boolean. If it succeeds, the boolean is
    # returned. If it fails, a ValueError is raised.

    # If it's already a boolean, just return it.
    if param_value is True or param_value is False or param_value is None:
        return param_value
    # Tries to accept a variety of conventions for True or False.
    elif param_value.lower() in ("true", "t", "yes", "1"):
        return True
    elif param_value.lower() in ("false", "f", "no", "0"):
        return False
    else:
        raise ValueError(
            f"parameter {param_name}: the supplied parameter value "
            + f"'{param_value}' does not parse as either True or False"
        )


def gen_crt_updt_argd(model_class, request_json, **argd):
    """
    Accepts a SQLAlchemy.Model subclass and a request.json object and
    returns a dict of parameter key/value pairs, whose values have been
    validated, that can be used as an argument to crt_model_obj() or
    updt_model_obj().

    :model_class: A SQLAlchemy.Model subclass class object, the target
    to build constructor/update arguments for.
    :request_json: The value of request.json during the execution of a
    flask endpoint function, containing the key-value pairs to convert
    to constructor/update arguments.
    :**argd: (Optional.) A single key/value pair, where the key is the
    name of a foreign key in the relevant table, and the value is the
    value for that key supplied to the flask endpoint function as a
    URL argument. If the value for that column in request.json, it is
    replaced with the value.
    :return: A dict that can be constructor/update arguments for the
    SQLAlchemy.Model subclass target.
    """

    # An argument to _validate_date for Book, predefined for easier
    # reading.
    tm_date_str = (date.today() + timedelta(days=1)).isoformat()

    # A dispatch table for code to generate arguments for a given
    # SQLAlchemy model subclass's constructor.
    #
    # The keys are the model subclasses themselves; the values are
    # lambdas that take a dict of the JSON from a request, and return a
    # dict of the corresponding constructor's arguments which have been
    # validated.

    # Extracts & validates the arguments for the Author constructor.
    def to_author_argd(req):
        return dict(
            first_name=_validate_str("first_name", req.get("first_name")),
            last_name=_validate_str("last_name", req.get("last_name")),
        )

    # Extracts & validates the arguments for the AuthorMetadata constructor.
    def to_author_metadata_argd(req):
        return dict(
            author_id=_validate_int("author_id", req.get("author_id")),
            age=_validate_int("age", req.get("age"), 18, 120),
            biography=_validate_str("biography", req.get("biography"), 1, math.inf),
            photo_res_horiz=_validate_int(
                "photo_res_horiz", req.get("photo_res_horiz"), 1
            ),
            photo_res_vert=_validate_int(
                "photo_rest_vert", req.get("photo_res_vert"), 1
            ),
            photo_url=_validate_str("photo_url", req.get("photo_url"), 1, 256),
        )

    # Extracts & validates the arguments for the Book constructor.
    def to_book_argd(req):
        return dict(
            editor_id=_validate_int("editor_id", req.get("editor_id"), 0),
            series_id=_validate_int("series_id", req.get("series_id"), 0),
            title=_validate_str("title", req.get("title")),
            publication_date=_validate_date(
                "publication_date", req.get("publication_date"), "1990-01-01"
            ),
            edition_number=_validate_int(
                "edition_number", req.get("edition_number"), 1, 10
            ),
            is_in_print=_validate_bool("is_in_print", req.get("is_in_print")),
        )

    # Extracts & validates the arguments for the Manuscript constructor.
    def to_manuscript_argd(req):
        return dict(
            editor_id=_validate_int("editor_id", req.get("editor_id"), 0),
            series_id=_validate_int("series_id", req.get("series_id"), 0),
            working_title=_validate_str("working_title", req.get("working_title")),
            due_date=_validate_date(
                "due_date",
                req.get("due_date"),
                tm_date_str,
                date(date.today().year + 2, date.today().month, 1).isoformat(),
            ),
            advance=_validate_int("advance", req.get("advance"), 5000, 100000),
        )

    # Extracts & validates the arguments for the Client constructor.
    def to_client_argd(req):
        return dict(
            salesperson_id=_validate_int(
                "salesperson_id", req.get("salesperson_id"), 0
            ),
            email_address=_validate_str("email_address", req.get("email_address")),
            phone_number=_validate_str("phone_number", req.get("phone_number"), 11, 11),
            business_name=_validate_str("business_name", req.get("business_name")),
            street_address=_validate_str("street_address", req.get("street_address")),
            city=_validate_str("city", req.get("city")),
            state=_validate_str("state", req.get("state"), 2, 2),
            zipcode=_validate_str("zipcode", req.get("zipcode"), 9, 9),
            country=_validate_str("country", req.get("country")),
        )

    # Extracts & validates the arguments for the Editor constructor.
    def to_editor_argd(req):
        return dict(
            first_name=_validate_str("first_name", req.get("first_name")),
            last_name=_validate_str("last_name", req.get("last_name")),
            salary=_validate_int("salary", req.get("salary"), 0),
        )

    # Extracts & validates the arguments for the Salesperson constructor.
    def to_salesperson_argd(req):
        return dict(
            first_name=_validate_str("first_name", req.get("first_name")),
            last_name=_validate_str("last_name", req.get("last_name")),
            salary=_validate_int("salary", req.get("salary"), 0),
        )

    # Extracts & validates the arguments for the Series constructor.
    def to_series_argd(req):
        return dict(
            title=_validate_str("title", req.get("title")),
            volumes=_validate_int("volumes", req.get("volumes"), 2),
        )

    to_argd_dispatch = {
        Author: to_author_argd,
        AuthorMetadata: to_author_metadata_argd,
        Book: to_book_argd,
        Manuscript: to_manuscript_argd,
        Client: to_client_argd,
        Editor: to_editor_argd,
        Salesperson: to_salesperson_argd,
        Series: to_series_argd,
    }

    # The lambda that computes the argd that can be constructor or
    # update arguments for the model_class arguments is located, and
    # called with request_json, so it evaluates.
    create_or_update_argd = to_argd_dispatch[model_class](request_json)

    # If the id_column and its value id_value are defined, and the
    # argd's value for a key of id_column is None, then it's set to
    # id_value. (If the JSON contains a different value than the one
    # included from the URL argument, it can override.)
    if len(argd):
        ((id_column_name, id_column_value),) = argd.items()
        if create_or_update_argd.get(id_column_name) is None:
            create_or_update_argd[id_column_name] = id_column_value
    return create_or_update_argd


def handle_exc(exception):
    """
    A generalized exception handler which implements an ideal handler
    for endpoint function try/except blocks.

    :exception: The exception being handled.
    :return: A flask.Response object. NB: May raise an exception rather
    than returning.
    """
    # If the exception is a 404 error, it's passed through unmodified.
    # (`from None` ensures it isn't modified by passing through this
    # try/except statement.)
    if isinstance(exception, werkzeug.exceptions.NotFound):
        raise exception from None

    # The validation logic that checks arguments uses ValueError to
    # indicate an invalid argument. So if it's a ValueError, that's a
    # 400; anything else is a coding error, a 500.
    status = 400 if isinstance(exception, ValueError) else 500

    # If the exception has a message, it's extracted and built into a
    # helpful text for the error;
    return Response("".join(traceback.format_exception(exception)), status)


def crt_tbl_row_clos(model_class):
    """
    Returns a function that executes an endpoint function POST /{table},
    using the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for outer table
    :return: a function that executes POST/{table}
    """

    def _internal_create_table_row(request_json):
        try:
            # Using crt_model_obj() to process request.json into a
            # model_class argument dict and instance a model_class
            # object.
            model_class_obj = crt_model_obj(
                model_class, gen_crt_updt_argd(model_class, request_json)
            )
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return handle_exc(exception)

    return _internal_create_table_row


def del_tbl_row_by_id_clos(model_class):
    """
    Returns a function that executes an endpoint function for DELETE
    /{table}/{id}, using the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for the table
    :returns: a function that executes DELETE/{table}/{id} The returned
    function:
    :model_id: The primary key value for the row to delete.
    :return: A flask.Response object.
    """

    def _internal_delete_table_row_by_id(model_id):
        try:
            del_model_obj(model_id, model_class)
            return jsonify(True)
        except Exception as exception:
            return handle_exc(exception)

    return _internal_delete_table_row_by_id


def del_tbl_row_by_id_foreign_key_clos(
    outer_class, outer_id_column, inner_class, inner_id_column
):
    """
    Returns a function that executes DELETE
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the
    supplied SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return: a function that executes DELETE
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The closure:

    :outer_id: a value for the primary key column in the outer table
    :inner_id: a value for the primary key column in the inner table;
    this row will be deleted
    :return: A flask.Response object.
    """

    def _internal_delete_table_row_by_id_and_foreign_key(outer_id, inner_id):
        try:
            # Verifying that a row in the outer table with a primary key
            # equal to outer_id exists, else it's a 404.
            outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a
            # foreign key from the outer table, else it's a 404.
            if not any(
                getattr(inner_class_obj, inner_id_column) == inner_id
                for inner_class_obj in inner_class.query.where(
                    getattr(inner_class, outer_id_column) == outer_id
                )
            ):
                return abort(404)

            # Deleting the row in the inner table with that foreign key.
            # If inner_class is Book or Manuscript, also cleans up the
            # authors_books or authors_manuscripts table.
            del_model_obj(inner_id, inner_class)
            return jsonify(True)
        except Exception as exception:
            return handle_exc(exception)

    return _internal_delete_table_row_by_id_and_foreign_key


def disp_tbl_rows_by_foreign_id_clos(outer_class, outer_id_column, inner_class):
    """
    Returns a function that executes an endpoint function for GET
    /{outer_table}/{outer_id}/{inner_table}, using the supplied
    SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table

    :return: a function that executes GET
    /{outer_table}/{outer_id}/{inner_table}

    The closure:

    :outer_id: a value for the primary key column in the outer table
    :return: A flask.Response object.
    """

    def _internal_display_table_rows_by_foreign_id(outer_id):
        try:
            outer_class.query.get_or_404(outer_id)
            # An outer_class object for every row in the inner_class
            # table with the given outer_id.
            retval = [
                inner_class_obj.serialize()
                for inner_class_obj in inner_class.query.where(
                    getattr(inner_class, outer_id_column) == outer_id
                )
            ]
            if not len(retval):
                return abort(404)
            return jsonify(retval)
        except Exception as exception:
            return handle_exc(exception)

    return _internal_display_table_rows_by_foreign_id


def disp_tbl_rows_clos(model_class):
    """
    Returns an endpoint function that executes GET /{table}, using the
    supplied SQLAlchemy.Model subclasses.

    :model_class: the Model subclass for the table
    :return: a function that executes GET /{table}

    The closure (takes no arguments):

    :return: a flask.Response object
    """

    def _internal_display_table_rows():
        try:
            result = [
                model_class_obj.serialize()
                for model_class_obj in model_class.query.all()
            ]
            return jsonify(result)
        except Exception as exception:
            return handle_exc(exception)

    return _internal_display_table_rows


def disp_tbl_row_by_id_clos(model_class):
    """
    Returns an endpoint function that executes GET /{table}/{id}, using
    the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for the table

    :return:      a function that executes GET /{table}/{id}
    The closure:

    :model_id: a value for the primary key column in the table
    :return: a flask.Response object
    """

    def _internal_display_table_row_by_id(model_id):
        try:
            model_class_obj = model_class.query.get_or_404(model_id)
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return handle_exc(exception)

    return _internal_display_table_row_by_id


def disp_tbl_row_by_id_foreign_key_clos(
    outer_class, outer_id_column, inner_class, inner_id_column
):
    """
    Returns an endpoint function that executes GET
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the
    supplied SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return: a function that executes GET
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The closure:

    :outer_id: a value for the primary key column in the outer table
    :inner_id: a value for the primary key column in the inner table;
    this row will be deleted
    :return: a flask.Response object
    """

    def _internal_display_table_row_by_id_and_foreign_key(outer_id, inner_id):
        try:
            outer_class.query.get_or_404(outer_id)
            # An inner_class object for every row in the inner_class
            # table with the given outer_id.
            inner_class_objs = list(
                inner_class.query.where(
                    getattr(inner_class, outer_id_column) == outer_id
                )
            )
            # Iterating across the list looking for the inner_class
            # object with the given inner_class_id. If it's found, it's
            # serialized and returned. Otherwise, a 404 error is raised.
            for inner_class_obj in inner_class_objs:
                if getattr(inner_class_obj, inner_id_column) == inner_id:
                    return jsonify(inner_class_obj.serialize())
            return abort(404)
        except Exception as exception:
            return handle_exc(exception)

    return _internal_display_table_row_by_id_and_foreign_key


def updt_tbl_row_by_id_clos(model_class):
    """
    Returns an endpoint function that executes PATCH /{table}/{id},
    using the supplied SQLAlchemy.Model subclass.

    :model_class: the Model subclass for the table
    :return: a function that executes GET /{table}/{id}

    The closure:

    :model_id: a value for the primary key column in the table
    :request_json: a reference to the request.json object available
    within the endpoint function
    :return: a flask.Response object
    """

    def _internal_update_table_row_by_id(model_id, request_json):
        try:
            # updt_model_obj is used to fetch and update the model class
            # object indicates by the model_class object and its id
            # value model_id. gen_crt_updt_argd() is used to build
            # its param dict argument.
            model_class_obj = updt_model_obj(
                model_id,
                model_class,
                gen_crt_updt_argd(model_class, request_json),
            )
            db.session.add(model_class_obj)
            db.session.commit()
            return jsonify(model_class_obj.serialize())
        except Exception as exception:
            return handle_exc(exception)

    return _internal_update_table_row_by_id


def updt_tbl_row_by_id_foreign_key_clos(
    outer_class, outer_id_column, inner_class, inner_id_column
):
    """
    Returns an endpoint function that executes PATCH
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}, using the
    supplied SQLAlchemy.Model subclasses.

    :outer_class: the Model subclass for the outer table
    :inner_class: the Model subclass for the inner table
    :return: a function that executes PATCH
    /{outer_table}/{outer_id}/{inner_table}/{inner_id}

    The closure:

    :outer_id: a value for the primary key column in the outer table
    :inner_id: a value for the primary key column in the inner table;
    this row will be deleted
    :request_json: a reference to the request.json object available
    within the endpoint function
    :return: a flask.Response object
    """

    def _internal_update_table_row_by_id_and_foreign_key(
        outer_id, inner_id, request_json
    ):
        try:
            # Verifying that a row in the outer table with a primary key
            # equal to outer_id exists, else it's a 404.
            outer_class.query.get_or_404(outer_id)

            # Verifying that a row exists in the inner table with a
            # foreign key from the outer table, else it's a 404.
            if not any(
                getattr(inner_class_obj, inner_id_column) == inner_id
                for inner_class_obj in inner_class.query.where(
                    getattr(inner_class, outer_id_column) == outer_id
                )
            ):
                return abort(404)

            # Using updt_model_obj() to fetch the inner_class object and
            # update it against request.json.
            inner_class_obj = updt_model_obj(
                inner_id,
                inner_class,
                gen_crt_updt_argd(
                    inner_class, request_json, **{outer_id_column: outer_id}
                ),
            )
            db.session.add(inner_class_obj)
            db.session.commit()
            return jsonify(inner_class_obj.serialize())
        except Exception as exception:
            return handle_exc(exception)

    return _internal_update_table_row_by_id_and_foreign_key


def check_json_req_props(
    sqlal_model_cls,
    request_json,
    excl_cols=frozenset(),
    optional_cols=frozenset(),
    chk_missing=True,
    chk_unexp=True,
):
    """
    Checks the dict equivalent of a JSON object that's expected to
    consist of some or all the properties needed to define one of the
    SQLAlchemy model subclass objects. Raises a ValueError if the JSON
    object contains properties that aren't associated with the model
    subclass, or doesn't include properties needed to instance the model
    subclass. Otherwise returns True.

    :sqlal_model_cls: The SQLAlchemy model subclass to test the JSON
    object as valid arguments for creating or modifying an instance of.
    :request_json: The dict equivalent of the JSON object that was
    submitted via POST data to test.
    :excl_cols: An optional argument of columns to treat as unexpected;
    typically used for *_id columns since submitted JSON shouldn't
    dictate an id.
    :optional_cols: An optional argument of columns to treat as
    optional-- i.e. to accept either the presence or absence of without
    raising a ValueError.
    :chk_missing: A boolean that if false supresses checks for missing
    properties.
    :return: If a ValueError is not raised, returns True.
    """

    # A utility function that converts a list of keys into an English
    # expression listing the keys, for an error message.
    def _prop_expr(keys_list):
        match len(keys_list):
            case 1:
                return f"property '{keys_list[0]}'"
            case 2:
                return f"properties '{keys_list[0]}' and '{keys_list[1]}'"
            case _:
                return (
                    "properties '"
                    + "', '".join(keys_list[:-1])
                    + f"', and '{keys_list[-1]}'"
                )

    # Collect the two set of properties.
    request_json_prop = set(request_json.keys())
    columns = set(map(attrgetter("name"), sqlal_model_cls.__table__.columns))
    expected_prop = columns - excl_cols
    if expected_prop == request_json_prop:
        return True

    # If the two sets didn't match, work out which combination of
    # unexpected and missing properties happened and raise the
    # appropriate error.
    #
    # Since failing this function's tests is most likely to happen
    # because an entirely different kind of object was POSTed, if both
    # unexpected and missing properties happened a combined exception
    # with both issues is raised.
    errors = list()
    missing_prop = expected_prop - request_json_prop - optional_cols
    unexpected_prop = request_json_prop - expected_prop - optional_cols

    if chk_missing and len(missing_prop):
        errors.append(
            "Request missing expected " + _prop_expr(sorted(missing_prop)) + "."
        )
    if chk_unexp and len(unexpected_prop):
        errors.append(
            "Request included unexpected " + _prop_expr(sorted(unexpected_prop)) + "."
        )

    match len(errors):
        case 0:
            return True
        case 1:
            raise ValueError(errors[0])
        case 2:
            raise ValueError(f"{errors[0]} {errors[1]}")
