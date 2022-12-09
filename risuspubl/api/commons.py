#!/usr/bin/python3

import math
from datetime import date

from risuspubl.dbmodels import Authors_Manuscripts, Authors_Books, Book, Client, Editor, Manuscript, Salesperson, SalesRecord, Series, db


# This lookup table associates a *_id param name with the SQLAlchemy.Model
# subclass class object representing the table where a column by that name is
# the primary key. Used to validate whether a parameter with such a name has a
# value that is associated with a row in that table.
id_params_to_model_subclasses = {'book_id': Book, 'client_id': Client, 'editor_id': Editor, 'manuscript_id': Manuscript,
                              'sales_record_id': SalesRecord, 'salesperson_id': Salesperson, 'series_id': Series}


def update_model_obj(id_val, model_subclass, params_to_types_args_values):
    """
    This function updates a SQLAlchemy.Model subclass object. It uses the id
    value and Model subclass class object to look up a model object, and then
    uses the dict of parameter names, values, and validator instructions to
    update the column values on that object. Then the object is returned.

    :model_subclass:              An SQLAlchemy.Model subclass class object,
                                  the class to instance an object of.
    :params_to_types_args_values: A dict whose keys are param names and whose
                                  values are 3-tuples comprised of the type of
                                  the param value, a tuple of arguments for the
                                  validator function for that type, and the
                                  value for that parameter (can be None).
    :return:                      An instance of the class that was the first
                                  argument.
    """
    model_obj = model_subclass.query.get_or_404(id_val)
    # If all the dict's param_value slots are None, this update can't proceed bc
    # there's nothing to update, so a ValueError is raised.
    if all(param_value is None for _, _, param_value in params_to_types_args_values.values()):
        raise ValueError('update action executed with no parameters indicating fields to update')
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        if param_value is None:
            continue
        if param_name.endswith('_id'):
            # This step matches a *_id parameters with the Model class for the
            # table where that column is a primary key, and does a get() to
            # confirm the *_id value corresponds to a row in that table. If not,
            # a ValueError is raised.
            id_model_subclass = id_params_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        # The validator for this data type is located and applied with the given
        # arguments. All of this module's validators are passthroughs: they
        # accept the value as an argument and return the value after processing;
        # in the case of int and float they've casted the value to its proper
        # type. date values are returned as strings because that's the format
        # that a SQLAlchemy.Model subclass's Date columns accept values in.
        validator = types_to_validators[param_type]
        setattr(model_obj, param_name, validator(param_name, param_value, *validator_args))
    return model_obj


def create_model_obj(model_subclass, params_to_types_args_values, optional_params=set()):
    """
    This function builds an SQLAlchemy.Model subclass object. It uses the Model
    subclass class object and the dict of parameter names, values, and validator
    instructions to build a dict of arguments to the Model subclass constructor,
    instantiates an object and returns it.

    :model_subclass:              An SQLAlchemy.Model subclass class object,
                                  the class to instance an object of.
    :params_to_types_args_values: A dict whose keys are param names and whose
                                  values are 3-tuples comprised of the type of
                                  the param value, a tuple of arguments for the
                                  validator function for that type, and the
                                  value for that parameter.
    :optional_params:             An optional argument, a set of parameter names
                                  that are not required for the constructor. If
                                  the value of one of these parameters is None,
                                  it's skipped. If a parameter does NOT occur
                                  in this set and it's None, a ValueError is
                                  raised.
    :return:                      An instance of the class that was the first
                                  argument.
    """
    model_obj_args = dict()
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        # optional_params is the list of names of parameters that may be None.
        if param_value is None and param_name in optional_params:
            continue
        # If a required param is none, a ValueError is raised.
        elif param_value is None:
            raise ValueError(f"required parameter '{param_name}' not present")
        if param_name.endswith('_id'):
            # This step matches a *_id parameters with the Model class for the
            # table where that column is a primary key, and does a get() to
            # confirm the *_id value corresponds to a row in that table. If not,
            # a ValueError is raised.
            id_model_subclass = id_params_to_model_subclasses[param_name]
            if id_model_subclass.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f'the `{id_model_subclass.__tablename__}` table')
        # The validator for this data type is located and applied with the given
        # arguments. All of this module's validators are passthroughs: they
        # accept the value as an argument and return the value after processing;
        # in the case of int and float they've casted the value to its proper
        # type. date values are returned as strings because that's the format
        # that a SQLAlchemy.Model subclass's Date columns accept values in.
        validator = types_to_validators[param_type]
        model_obj_args[param_name] = validator(param_name, param_value, *validator_args)
    return model_subclass(**model_obj_args)


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


def validate_date(param_name, param_value, lower_bound='1900-01-01', upper_bound=date.today().isoformat()):
    """
    This function parses a param value to a date, and tests if it falls within
    lower and upper bounds. If it succeeds, the param value string is returned.
    If it fails, a ValueError is raised.

    :param_name:  The name of the JSON parameter. Used in the ValueError exception
                  message if one is raised.
    :param_value: The value of the JSON parameter, a string.
    :lower_bound: The lower bound that the float value is tested against; must
                  be greater than or equal to. Defaults to 1900-01-01.
    :upper_bound: The upper bound that the float value is tested against; must
                  be less than or equal to. Defaults to today's date, in
                  YYYY-MM-DD format.
    :return:      A string, the original param value.
    """
    try:
        param_date_obj = date.fromisoformat(param_value)
    except ValueError as exception:
        # Attempting to parse the date using datetime.date.fromisoformat() is
        # the fastest way to find out if it's a legal date. Its error message
        # is fine to use, but the parameter name and value are prepended so the
        # message is up to standards.
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


def validate_int(param_name, param_value, lower_bound=-math.inf, upper_bound=math.inf):
    """
    This function parses a param value to an int, and tests if it falls within
    lower and upper bounds. If it succeeds, the int is returned. If it fails, a
    ValueError is raised.

    :param_name:  The name of the JSON parameter. Used in the ValueError exception
                  message if one is raised.
    :param_value: The value of the JSON parameter, a string.
    :lower_bound: The lower bound that the float value is tested against; must
                  be greater than or equal to. Defaults to -Infinity.
    :upper_bound: The upper bound that the float value is tested against; must
                  be less than or equal to. Defaults to +Infinity.
    :return:      An int, parsed from the param value.
    """
    param_int_value = int(param_value)
    if not (lower_bound <= param_int_value <= upper_bound):
        raise ValueError(f"parameter {param_name}: supplied integer value '{param_int_value}' does not fall between "
                         f'[{lower_bound}, {upper_bound}]')
    return param_int_value


def validate_float(param_name, param_value, lower_bound=-math.inf, upper_bound=math.inf):
    """
    This function parses a param value to a float, and tests if it falls within
    lower and upper bounds. If it succeeds, the float is returned. If it fails,
    a ValueError is raised.

    :param_name:  The name of the JSON parameter. Used in the ValueError exception
                  message if one is raised.
    :param_value: The value of the JSON parameter, a string.
    :lower_bound: The lower bound that the float value is tested against; must
                  be greater than or equal to. Defaults to -Infinity.
    :upper_bound: The upper bound that the float value is tested against; must
                  be less than or equal to. Defaults to +Infinity.
    :return:      A float, parsed from the param value.
    """
    try:
        param_float_value = float(param_value)
    except ValueError:
        raise ValueError(f"parameter {param_name}: value {param_value} doesn't parse as a floating point number")
    if not (lower_bound <= param_float_value <= upper_bound):
        raise ValueError(f"parameter {param_name}: supplied float value '{param_float_value}' does not fall between "
                         f'[{lower_bound}, {upper_bound}]')
    return param_float_value


def validate_str(param_name, param_value, lower_bound=1, upper_bound=64):
    """
    This function tests if a param value string's length falls between lower
    and upper bounds. If it succeeds, the string is returned. If it fails, a
    ValueError is raised.

    :param_name:  The name of the JSON parameter. Used in the ValueError exception
                  message if one is raised.
    :param_value: The value of the JSON parameter, a string.
    :lower_bound: The lower bound on the value's length, default 1.
    :upper_bound: The upper bound on the value's length, default 64.
    :return:      A string, the param_value unmodified.
    """
    if not (lower_bound <= len(param_value) <= upper_bound):
        # If the reason for failure is the str is length zero, a more specific
        # error message is used.
        if len(param_value) == 0:
            raise ValueError(f'parameter {param_name}: may not be zero-length')
        # If the upper and lower bounds are equal, that's a requirement the
        # string be that length, so the error message states that.
        elif lower_bound == upper_bound:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{param_value}' is not "
                             f'equal to {lower_bound}')
        else:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{param_value}' does not "
                             f'fall between [{lower_bound}, {upper_bound}]')
    return param_value


def validate_bool(param_name, param_value):
    """
    This function parses a param value to a boolean. If it succeeds, the boolean
    is returned. If it fails, a ValueError is raised.

    :param_name:  The name of the JSON parameter. Used in the ValueError exception
                  message if one is raised.
    :param_value: The value of the JSON parameter, a string.
    :return:      A boolean, parsed from the param_value.
    """
    if isinstance(param_value, bool):
        return param_value
    elif param_value.lower() in ('true', 't', 'yes', '1'):    # Tries to accept a variety
        return True                                         # of conventions for a True
    elif param_value.lower() in ('false', 'f', 'no', '0'):  # boolean or a False boolean.
        return False
    else:
        raise ValueError(f"parameter {param_name}: the supplied parameter value '{param_value}' does not parse as either "
                         'True or False')


# This lookup table associates a type object to the validator function for that
# data type. It's defined at the end of the file so that all the function names
# are defined. It's used by functions at the top of the file, but thanks to lazy
# evaluation they'll have access to it even though it's defined here.
types_to_validators = {int: validate_int, bool: validate_bool, str: validate_str, date: validate_date,
                       float: validate_float}
