#!/usr/bin/python3

import math
import re

from datetime import date

from risuspubl.dbmodels import *


id_params_to_model_classes = {'book_id': Book, 'client_id': Client, 'editor_id': Editor, 'manuscript_id': Manuscript,
                              'sales_record_id': SalesRecord, 'salesperson_id': Salesperson, 'series_id': Series}


def update_model_obj(id_val, model_class, params_to_types_args_values):
    model_obj = model_class.query.get_or_404(id_val)
    if all(param_value is None for _, _, param_value in params_to_types_args_values.values()):
        raise ValueError('update action executed with no parameters indicating fields to update')
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        if param_value is None:
            continue
        if param_name.endswith('_id'):
            id_model_class = id_params_to_model_classes[param_name]
            if id_model_class.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f"the `{id_model_class.__tablename__}` table")
        validator = types_to_validators[param_type]
        setattr(model_obj, param_name, validator(param_name, param_value, *validator_args))
    return model_obj


def create_model_obj(model_class, params_to_types_args_values, optional_params=set()):
    model_obj_args = dict()
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        if param_value is None and param_name in optional_params:
            continue
        elif param_value is None:
            raise ValueError(f"required parameter '{param_name}' not present")
        if param_name.endswith('_id'):
            id_model_class = id_params_to_model_classes[param_name]
            if id_model_class.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in "
                                 f"the `{id_model_class.__tablename__}` table")
        validator = types_to_validators[param_type]
        model_obj_args[param_name] = validator(param_name, param_value, *validator_args)
    return model_class(**model_obj_args)


def delete_model_obj(id_val, model_class):
    model_obj = model_class.query.get_or_404(id_val)
    if model_class is Book:
        ab_del = Authors_Books.delete().where(Authors_Books.columns[1] == id_val)
        db.session.execute(ab_del)
        db.session.commit()
    elif model_class is Manuscript:
        am_del = Authors_Manuscript.delete().where(Authors_Manuscript.columns[1] == id_val)
        db.session.execute(am_del)
        db.session.commit()
    db.session.delete(model_obj)
    db.session.commit()


month_lengths = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

date_col_re = re.compile(r'^(\d\d\d\d)-(\d\d)-(\d\d)$')


def validate_date(param_name, date_str, lowerb='1900-01-01', upperb=date.today().isoformat()):
    re_match = date_col_re.match(date_str)
    if not re_match:
        raise ValueError(f"parameter {param_name}: supplied date value '{date_str}' does not match the pattern "
                         "YYYY-MM-DD")
    year, month, day = map(int, re_match.groups())
    is_leap_year = False if year % 4 != 0 else \
                   True if year % 100 != 0 else \
                   False if year % 400 != 0 else True
    if not (1 <= month <= 12):
        raise ValueError(f"parameter {param_name}: supplied date value '{date_str}' month does not fall between "
                         "[1, 12]")
    if is_leap_year and month == 2 and not 1 <= day <= 29:
        raise ValueError(f"parameter {param_name}: supplied date value '{date_str}' day value does not fall between "
                         "[1, 29]")
    elif not (1 <= day <= month_lengths[month]):
        raise ValueError(f"parameter {param_name}: supplied date value '{date_str}' day value does not fall between "
                         f"[1, {month_lengths[month]}]")
    lowerb = date.fromisoformat(lowerb)
    upperb = date.fromisoformat(upperb)
    dateval = date.fromisoformat(date_str)
    if not (lowerb <= dateval <= upperb):
        raise ValueError(f"parameter {param_name}: supplied date value '{date_str}' does not fall between "
                         f"[{lowerb}, {upperb}]")
    return date_str


def validate_int(param_name, strval, lowerb=-math.inf, upperb=math.inf):
    intval = int(strval)
    if not (lowerb <= intval <= upperb):
        raise ValueError(f"parameter {param_name}: supplied integer value '{intval}' does not fall between "
                         f"[{lowerb}, {upperb}]")
    return intval


def validate_float(param_name, strval, lowerb=-math.inf, upperb=math.inf):
    floatval = float(strval)
    if not (lowerb <= floatval <= upperb):
        raise ValueError(f"parameter {param_name}: supplied float value '{floatval}' does not fall between "
                         f"[{lowerb}, {upperb}]")
    return floatval


def validate_str(param_name, strval, lowerb=1, upperb=64):
    if not (lowerb <= len(strval) <= upperb):
        if len(strval) == 0:
            raise ValueError(f"parameter {param_name}: may not be zero-length")
        elif lowerb == upperb:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{strval}' is not equal "
                             f"to {lowerb}")
        else:
            raise ValueError(f"parameter {param_name}: the length of supplied string value '{strval}' does not fall "
                             f"between [{lowerb}, {upperb}]")
    return strval


def validate_bool(param_name, strval):
    if strval.lower() in ('true', 't', 'yes', '1'):
        return True
    elif strval.lower() in ('false', 'f', 'no', '0'):
        return False
    else:
        raise ValueError(f"parameter {param_name}: the supplied parameter value '{strval}' does not parse as either "
                         "True or False")


types_to_validators = {int: validate_int, bool: validate_bool, str: validate_str, date: validate_date,
                       float: validate_float}
