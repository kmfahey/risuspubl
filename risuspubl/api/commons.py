#!/usr/bin/python3

import re
import math

from datetime import date

from flask import abort

from risuspubl.dbmodels import *


id_params_to_model_classes = {'book_id': Book, 'client_id': Client, 'editor_id': Editor, 'manuscript_id': Manuscript,
                              'sales_record_id': SalesRecord, 'salesperson_id': Salesperson, 'series_id': Series}


def update_model_obj(id_val, model_class, params_to_types_args_values):
    model_obj = model_class.query.get_or_404(id_val)
    for param_name, (param_type, validator_args, param_value) in params_to_types_args_values.items():
        if param_value is None:
            continue
        if param_name.endswith('_id'):
            id_model_class = id_params_to_model_classes[param_name]
            if id_model_class.query.get(param_value) is None:
                return abort(400)
        validator = types_to_validators[param_type]
        setattr(model_obj, param_name, validator(param_value, *validator_args))
    return model_obj


def create_model_obj(model_class, params_to_types_args_values, optional_params=()):
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
                return abort(400)
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

date_col_re = re.compile("^(\d\d\d\d)-(\d\d)-(\d\d)$")

def validate_date(date_str, lowerb="1900-01-01", upperb=date.today().isoformat()):
    re_match = date_col_re.match(date_str)
    if not re_match:
        raise ValueError()
    year, month, day = map(int, re_match.groups())
    is_leap_year = False if year % 4 != 0 else \
                   True if year % 100 != 0 else \
                   False if year % 400 != 0 else True
    if not (1990 <= year <= 2025):
        raise ValueError()
    if not (1 <= month <= 12):
        raise ValueError()
    if not (1 <= day <= month_length[month-1]):
        if not (is_leap_year and month == 2 and day == 29):
            raise ValueError()
    lowerb = date.fromisoformat(lowerb)
    upperb = date.fromisoformat(upperb)
    dateval = date.fromisoformat(date_str)
    if not (lowerb <= dateval <= upperb):
        raise ValueError()
    return date_str


def validate_int(strval, lowerb=-math.inf, upperb=math.inf):
    intval = int(strval)
    if not (lowerb <= intval <= upperb):
        raise ValueError()
    return intval


def validate_float(strval, lowerb=-math.inf, upperb=math.inf):
    floatval = float(strval)
    if not (lowerb <= floatval <= upperb):
        raise ValueError()
    return floatval


def validate_str(strval, lowerb=1, upperb=64):
    if not (lowerb <= len(strval) <= upperb):
        raise ValueError(strval)
    return strval


def validate_bool(strval):
    if strval.lower() in ("true", "t", "yes", "1"):
        return True
    elif strval.lower() in ("false", "f", "no", "0"):
        return False
    else:
        raise ValueError()


types_to_validators = {int: validate_int, bool: validate_bool, str: validate_str, date: validate_date, float: validate_float}

