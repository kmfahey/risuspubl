#!/usr/bin/python3

import flask
import csv
import os
import os.path
import collections
import pprint
import random
import datetime

from risuspubl.dbmodels import *



table_names = [
"authors_manuscripts", # X
"authors_books", # X
"books", # X
"authors", # X
"manuscripts", # X
"editors", # X
"clients", # X
"salespeople", # X
"sales_records", # X
"series" # X
               ]

table_to_id_column = {"authors": "author_id", "books": "book_id", "clients": "client_id", "editors": "editor_id",
                      "manuscripts": "manuscript_id", "sales_records": "sales_record_id",
                      "salespeople": "salesperson_id", "series": "series_id"}

table_to_model_class = {'authors': Author, 'books': Book, 'clients': Client, 'editors': Editor, 'manuscripts': Manuscript,
                      'sales_records': SalesRecord, 'salespeople': Salespeople, 'series': Series}

model_objs = collections.defaultdict(list)

model_ids = collections.defaultdict(list)

data_dir = "./data/"


def main():
    app = create_app()
    app.app_context().push()

    db = SQLAlchemy(app)

    truncate_tables(db)

    model_objs["authors"].extend(read_file_get_model_objs("authors", table_to_model_class["authors"]))
    model_ids["authors"].extend(commit_model_objs_get_ids("authors", model_objs["authors"], db))

    model_objs["editors"].extend(read_file_get_model_objs("editors", table_to_model_class["editors"]))
    model_ids["editors"].extend(commit_model_objs_get_ids("editors", model_objs["editors"], db))

    model_objs["series"].extend(read_file_get_model_objs("series", table_to_model_class["series"]))
    model_ids["series"].extend(commit_model_objs_get_ids("series", model_objs["series"], db))

    model_objs["books"].extend(read_file_get_model_objs("books", table_to_model_class["books"]))

    used_book_objs_by_id = dict()

    for series_obj in model_objs["series"]:
        series_obj.volumes = random.randint(2,5)
        for i in range(0, series_obj.volumes):
            book_obj = random.choice(model_objs["books"])
            while book_obj.series_id is not None:
                book_obj = random.choice(model_objs["books"])
            book_obj.series_id = series_obj.series_id
    for book_obj in model_objs["books"]:
        editor_obj = random.choice(model_objs["editors"])
        book_obj.editor_id = editor_obj.editor_id
        db.session.add(book_obj)
    db.session.commit()

    for book_obj in model_objs["books"]:
        author_objs = ((random.choice(model_objs["authors"]),) if random.random() < 0.85 else
                           (random.choice(model_objs["authors"]), random.choice(model_objs["authors"])))
        while len(author_objs) == 2 and author_objs[0].author_id == author_objs[1].author_id:
            author_objs = (random.choice(model_objs["authors"]), random.choice(model_objs["authors"]))
        for author_obj in author_objs:
            ab_insert = Authors_Books.insert().values(author_id=author_obj.author_id, book_id=book_obj.book_id)
            db.session.execute(ab_insert)
    db.session.commit()

    model_objs["manuscripts"].extend(read_file_get_model_objs("manuscripts", table_to_model_class["manuscripts"]))

    for manuscript_obj in model_objs["manuscripts"]:
        if random.random() < 1/6:
            series_obj = random.choice(model_objs["series"])
            manuscript_obj.series_id = series_obj.series_id
        editor_obj = random.choice(model_objs["editors"])
        manuscript_obj.editor_id = editor_obj.editor_id
        db.session.add(manuscript_obj)
    db.session.commit()

    for manuscript_obj in model_objs["manuscripts"]:
        author_objs = ((random.choice(model_objs["authors"]),) if random.random() < 0.85 else
                           (random.choice(model_objs["authors"]), random.choice(model_objs["authors"])))
        while len(author_objs) == 2 and author_objs[0].author_id == author_objs[1].author_id:
            author_objs = (random.choice(model_objs["authors"]), random.choice(model_objs["authors"]))
        for author_obj in author_objs:
            am_insert = Authors_Manuscripts.insert().values(author_id=author_obj.author_id, manuscript_id=manuscript_obj.manuscript_id)
            db.session.execute(am_insert)
    db.session.commit()

    model_objs["salespeople"].extend(read_file_get_model_objs("salespeople", table_to_model_class["salespeople"]))
    model_ids["salespeople"].extend(commit_model_objs_get_ids("salespeople", model_objs["salespeople"], db))

    model_objs["clients"].extend(read_file_get_model_objs("clients", table_to_model_class["clients"]))

    for client_obj in model_objs["clients"]:
        salesperson_obj = random.choice(model_objs["salespeople"])
        client_obj.salesperson_id = salesperson_obj.salesperson_id
        db.session.add(client_obj)
    db.session.commit()

    for book_obj in model_objs["books"]:
        start_date = datetime.date.fromisoformat(str(book_obj.publication_date))
        if book_obj.is_in_print:
            end_date = datetime.date.today()
        else:
            end_date = datetime.date.fromisoformat(generate_random_date(1)[0])
        profit_margin = random.uniform(0.075, 0.125)
        for year, month in generate_year_month_span(start_date.year, start_date.month, end_date.year, end_date.month):
            copies_sold = round(random.gauss(1050/12, 250/12))
            gross_profit = copies_sold_to_gross_profit(copies_sold)
            net_profit = round(gross_profit*profit_margin, 2)
            sales_record_args = dict(book_id=book_obj.book_id, year=year, month=month, copies_sold=copies_sold,
                                     gross_profit=gross_profit, net_profit=net_profit)
            sales_record_obj = SalesRecord(**sales_record_args)
            model_objs["sales_records"].append(sales_record_obj)
            db.session.add(sales_record_obj)
        db.session.commit()


def generate_year_month_span(startyear, startmonth, endyear, endmonth):
    year_month_pairs = list()
    for this_year in range(startyear, endyear+1):
        this_startmonth = startmonth if this_year == startyear else 1
        this_endmonth = endmonth if this_year == endyear else 12
        for this_month in range(this_startmonth, this_endmonth+1):
            year_month_pairs.append((this_year, this_month))
    return year_month_pairs

def copies_sold_to_gross_profit(copies_sold):
    gross_profit = 0
    for i in range(0,copies_sold):
        gross_profit += round(random.gauss((20+5)/2, 5), 2)
    gross_profit = round(gross_profit, 2)
    return gross_profit

def generate_random_date(number):
    month_length = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    is_leap_year = (lambda year: False if year % 4 != 0 else
                                 True if year % 100 != 0 else
                                 False if year % 400 != 0 else True)
    retval = list()
    for i in range(0,number):
        month = random.randint(1,18)
        year = random.randint(1990,2022)
        month = month % 12
        month = 12 if month == 0 else month
        if month == 2 and is_leap_year(year):
            day = random.randint(1,29)
        elif year == 2022 and month == 12:
            today = datetime.date.today()
            day = random.randint(1, today.day)
        else:
            day = random.randint(1, month_length[month-1])
        retval.append("%04i-%02i-%02i" % (year, month, day))
    return retval

def read_file_get_model_objs(table_name, model_class):
    csv_args = {"quotechar": '"', "delimiter": "\t", "skipinitialspace": True, "lineterminator": "\n",
                "quoting": csv.QUOTE_MINIMAL, "doublequote": True}
    file_path = os.path.join(data_dir, table_name + '.tsv')
    if not os.path.exists(file_path):
        raise FileNotFoundError("unable to locate file " + file_path)
    file_obj = open(file_path, 'r')
    model_objs = list()
    tsv_reader = csv.reader(file_obj, **csv_args)
    columns = next(tsv_reader)
    for row in tsv_reader:
        model_args = dict(zip(columns, row))
        if table_name == "books":
            model_args["is_in_print"] = True if model_args["is_in_print"] == "True" else False
        model_obj = model_class(**model_args)
        model_objs.append(model_obj)
    return model_objs

def commit_model_objs_get_ids(table_name, model_objs, db):
    ids = list()
    for model_obj in model_objs:
        db.session.add(model_obj)
    db.session.commit()
    id_column = table_to_id_column[table_name]
    for model_obj in model_objs:
        ids.append(getattr(model_obj, id_column))
    return ids

def truncate_tables(db):
    #Delete all rows from database tables
    for table_name in table_names:
        db.session.execute("DELETE FROM " + table_name + ";")
    db.session.commit()

def create_app(test_config=None):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI="postgresql://postgres@localhost/risuspublishing",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


if __name__ == "__main__":
    main()
