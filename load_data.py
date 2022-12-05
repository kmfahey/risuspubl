#!/usr/bin/python3

import flask
import csv
import os
import os.path
import collections
import pprint

from risuspubl.dbmodels import *


table_to_model_class = {'authors': Author, 'books': Book, 'clients': Client, 'editors': Editor, 'manuscripts': Manuscript,
                      'sales_records': SalesRecord, 'salespeople': Salespeople, 'series': Series}

model_objs = collections.defaultdict(list)
model_ids = collections.defaultdict(list)

data_dir = "./data/"
csv_args = dict(quotechar='"', delimiter="\t", skipinitialspace=True, lineterminator="\n", quoting=csv.QUOTE_MINIMAL, doublequote=True)


def main():
    app = create_app()
    app.app_context().push()

    db = SQLAlchemy(app)

    truncate_tables(db)

    for filename in os.listdir(data_dir):
        if not filename.endswith('.tsv'):
            continue
        table_name = filename.split('.')[0]
        model_class = table_to_model_class[table_name]
        filepath = os.path.join(data_dir, filename)
        fileobj = open(filepath, 'r')
        tsv_reader = csv.reader(fileobj, **csv_args)
        columns = next(tsv_reader)
        for row in tsv_reader:
            model_args = dict(zip(columns, row))
            model_obj = model_class(**model_args)
            model_objs[table_name].append(model_obj)
            db.session.add(model_obj)
        db.session.commit()
        for model_obj in model_objs[table_name]:
            eponymous_id_column = table_name.rstrip('s') + "_id"
            id_val = getattr(model_obj, eponymous_id_column)
            model_ids[table_name].append(id_val)
    pprint.pprint(model_ids)


def truncate_tables(db):
    #Delete all rows from database tables
    db.session.execute(authors_books.delete())
    db.session.execute(authors_manuscripts.delete())
    Author.query.delete()
    Book.query.delete()
    Client.query.delete()
    Editor.query.delete()
    Manuscript.query.delete()
    SalesRecord.query.delete()
    Salespeople.query.delete()
    Series.query.delete()
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
