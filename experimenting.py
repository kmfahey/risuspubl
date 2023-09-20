#!/usr/bin/python3

import collections
import os

from flask import abort

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
from risuspubl.flaskapp import create_app


table_names = [
    "authors_manuscripts",
    "authors_books",
    "books",
    "authors",
    "manuscripts",
    "editors",
    "clients",
    "salespeople",
    "sales_records",
    "series",
]

table_to_id_column = {
    "authors": "author_id",
    "books": "book_id",
    "clients": "client_id",
    "editors": "editor_id",
    "manuscripts": "manuscript_id",
    "sales_records": "sales_record_id",
    "salespeople": "salesperson_id",
    "series": "series_id",
}

table_to_model_class = {
    "authors": Author,
    "books": Book,
    "clients": Client,
    "editors": Editor,
    "manuscripts": Manuscript,
    "sales_records": SalesRecord,
    "salespeople": Salesperson,
    "series": Series,
}

model_objs = collections.defaultdict(list)

model_ids = collections.defaultdict(list)

data_dir = "./data/"


app = create_app()
app.app_context().push()
