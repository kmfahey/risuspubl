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
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in the `{id_model_class.__tablename__}`")
        validator = types_to_validators[param_type]
        setattr(model_obj, param_name, validator(param_value, *validator_args))
    return model_obj


def create_model_obj(model_class, params_to_types_args_values, optional_params=set()):
    model_obj_args = dict()
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        if param_value is None:
            if param_name in optional_params:
                continue
            else:
                raise ValueError(f"required parameter '{param_name}' not present")
        if param_name.endswith('_id'):
            id_model_class = id_params_to_model_classes[param_name]
            if id_model_class.query.get(param_value) is None:
                raise ValueError(f"supplied '{param_name}' value '{param_value}' does not correspond to any row in the `{id_model_class.__tablename__}`")
        validator = types_to_validators[param_type]
        model_obj_args[param_name] = validator(param_value, *validator_args)
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


month_length = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

date_col_re = re.compile(r'^(\d\d\d\d)-(\d\d)-(\d\d)$')


def validate_date(date_str, lowerb='1900-01-01', upperb=date.today().isoformat()):
    re_match = date_col_re.match(date_str)
    if not re_match:
        raise ValueError(f"supplied date value '{date_str}' does not match the pattern YYYY-MM-DD")
    year, month, day = map(int, re_match.groups())
    is_leap_year = False if year % 4 != 0 else \
                   True if year % 100 != 0 else \
                   False if year % 400 != 0 else True
    if not (1990 <= year <= 2025):
        raise ValueError(f"supplied date value '{date_str}' year does not fall between [1990, 2025]")
    if not (1 <= month <= 12):
        raise ValueError(f"supplied date value '{date_str}' month does not fall between [1, 12]")
    if is_leap_year and month == 2 and not 1 <= day <= 29:
        raise ValueError(f"supplied date value '{date_str}' day value does not fall between [1, 29]")
    elif not (1 <= day <= month_length[month-1]):
        raise ValueError(f"supplied date value '{date_str}' day value does not fall between [1, {month_length[month-1]}]")
    lowerb = date.fromisoformat(lowerb)
    upperb = date.fromisoformat(upperb)
    dateval = date.fromisoformat(date_str)
    if not (lowerb <= dateval <= upperb):
        raise ValueError(f"supplied date value '{date_str}' does not fall between ['{lowerb}', '{upperb}']")
    return date_str


def validate_int(strval, lowerb=-math.inf, upperb=math.inf):
    intval = int(strval)
    if not (lowerb <= intval <= upperb):
        raise ValueError(f'supplied integer value "{intval}" does not fall between [{lowerb}, {upperb}]')
    return intval


def validate_float(strval, lowerb=-math.inf, upperb=math.inf):
    floatval = float(strval)
    if not (lowerb <= floatval <= upperb):
        raise ValueError(f'supplied float value "{intval}" does not fall between [{lowerb}, {upperb}]')
    return floatval


def validate_str(strval, lowerb=1, upperb=64):
    if not (lowerb <= len(strval) <= upperb):
        if lowerb == upperb:
            raise ValueError(f"the length of supplied string value '{intval}' is not equal to {lowerb}")
        else:
            raise ValueError(f"the length of supplied string value '{intval}' does not fall between [{lowerb}, {upperb}]")
    return strval


def validate_bool(strval):
    if strval.lower() in ('true', 't', 'yes', '1'):
        return True
    elif strval.lower() in ('false', 'f', 'no', '0'):
        return False
    else:
        raise ValueError(f"the supplied parameter value '{strval}' does not parse as either True or False")


types_to_validators = {int: validate_int, bool: validate_bool, str: validate_str, date: validate_date, float: validate_float}
