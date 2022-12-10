#!/usr/bin/python3

import collections
import csv
import os
import os.path
import random
from datetime import date, timedelta

from risuspubl.dbmodels import Author, Authors_Books, Authors_Manuscripts, Book, Client, Editor, Manuscript, \
        SalesRecord, Salesperson, Series, db
from risuspubl.flaskapp import create_app


# This list is used by delete_from_tables(). These names are in a particular
# order such that each table which has a foriegn key dependency on another table
# is *later in the list* than that table. That way, this list can be iterated
# across, executing DELETE FROM {table} for each one, without getting fouled up
# on a foreign key dependency error.
table_names = ['authors_manuscripts', 'authors_books', 'books', 'authors', 'manuscripts', 'editors', 'clients',
               'salespeople', 'sales_records', 'series']

# Associates table names with the SQLAlchemy.Model subclasses that implement
# them. Used when calling commit_model_objs_get_ids() to know what
# SQLAlchemy.Model subclass object to pass in as a 2nd argument.
table_to_model_class = {'authors': Author, 'books': Book, 'clients': Client, 'editors': Editor,
                        'manuscripts': Manuscript, 'sales_records': SalesRecord, 'salespeople': Salesperson,
                        'series': Series}

model_objs = collections.defaultdict(list)

model_ids = collections.defaultdict(list)

data_dir = './data/'


def main():
    app = create_app()
    app.app_context().push()

    delete_from_tables(db)

    # Loads the tsv data in data/authors.tsv and instantiate one Author object
    # per line, returning them as a list. They're stored to the model_objs dict.
    model_objs['authors'].extend(read_file_get_model_objs('authors'))

    # Takes every Author object from the previous step and stores them in the
    # database, returning a list of their newly assigned author_ids.
    model_ids['authors'].extend(commit_model_objs_get_ids('authors', model_objs['authors']))

    # Same again, with data/editors.tsv and the Editor class.
    model_objs['editors'].extend(read_file_get_model_objs('editors'))
    model_ids['editors'].extend(commit_model_objs_get_ids('editors', model_objs['editors']))

    # Same again, with data/series.tsv and the Series class.
    model_objs['series'].extend(read_file_get_model_objs('series'))
    model_ids['series'].extend(commit_model_objs_get_ids('series', model_objs['series']))

    # Converts data/books.tsv to an array of Book objects.
    model_objs['books'].extend(read_file_get_model_objs('books'))
    for book_obj in model_objs['books']:
        # Selects a random editor id and assigns it to the Book object. That
        # column is required for a Book object.
        book_obj.editor_id = random.choice(model_ids['editors'])
        db.session.add(book_obj)
    # Saves the Book objects to the database.
    db.session.commit()

    # Iterates across the list of existing Series objects, picking Book objects
    # at random and setting the optional series_id column to that Series
    # object's series_id. Then saves the Book objects again.
    used_book_objs_ids = set()
    for series_obj in model_objs['series']:
        series_obj.volumes = random.randint(2, 5)
        for i in range(0, series_obj.volumes):
            book_obj = random.choice(model_objs['books'])
            # Can't reuse a Book object or use one that already has a series_id,
            # pick again.
            while book_obj.book_id in used_book_objs_ids or book_obj.series_id is not None:
                book_obj = random.choice(model_objs['books'])
            # Save used Book object ids to a set to track the objects that have
            # already been used.
            used_book_objs_ids.add(book_obj.book_id)
            book_obj.series_id = random.choice(model_ids['series'])
            db.session.add(book_obj)
        db.session.commit()

    # Creates a row in authors_books for every book, picking a random author_id (if
    # random() < 0.85) or a pair of random author_ids (otherwise).
    for book_obj in model_objs['books']:
        author_ids = ((random.choice(model_ids['authors']),) if random.random() < 0.85 else
                           (random.choice(model_ids['authors']), random.choice(model_ids['authors'])))
        # If two author_ids were picked but they're the same value, repeat until
        # two different values are picked.
        while len(author_ids) == 2 and author_ids[0] == author_ids[1]:
            author_ids = (random.choice(model_ids['authors']), random.choice(model_ids['authors']))
        # Create each new row in Authors_Books.
        for author_id in author_ids:
            ab_insert = Authors_Books.insert().values(author_id=author_id, book_id=book_obj.book_id)
            db.session.execute(ab_insert)
    db.session.commit()

    # Converts data/manuscripts.tsv to an array of Manuscript objects.
    model_objs['manuscripts'].extend(read_file_get_model_objs('manuscripts'))

    # Assigns a random editor_id to each Manuscript object, and (if random() <
    # ~0.166666) assigns a random series_id as well.
    for manuscript_obj in model_objs['manuscripts']:
        # If random() < 0.166666, assign a manuscript a series_id.
        if random.random() < 1/6:
            manuscript_obj.series_id = random.choice(model_ids['series'])
        manuscript_obj.editor_id = random.choice(model_ids['editors'])
        db.session.add(manuscript_obj)
    db.session.commit()

    # Creates a row in authors_manuscripts for every manuscript, picking a random author_id (if
    # random() < 0.85) or a pair of random author_ids (otherwise).
    for manuscript_obj in model_objs['manuscripts']:
        author_ids = ((random.choice(model_ids['authors']),) if random.random() < 0.85 else
                           (random.choice(model_ids['authors']), random.choice(model_ids['authors'])))
        # If two author_ids were picked but they're the same value, repeat until
        # two different values are picked.
        while len(author_ids) == 2 and author_ids[0] == author_ids[1]:
            author_ids = (random.choice(model_ids['authors']), random.choice(model_ids['authors']))
        # Create each new row in Authors_Manuscripts.
        for author_id in author_ids:
            am_insert = Authors_Manuscripts.insert().values(author_id=author_id, manuscript_id=manuscript_obj.manuscript_id)
            db.session.execute(am_insert)
    db.session.commit()

    # Converts data/salespeople.tsv to an array of Salesperson objects, saves them, and records their ids.
    model_objs['salespeople'].extend(read_file_get_model_objs('salespeople'))
    model_ids['salespeople'].extend(commit_model_objs_get_ids('salespeople', model_objs['salespeople']))

    model_objs['clients'].extend(read_file_get_model_objs('clients'))

    # Assigns a random salesperson_id to each Client object, then saves them.
    for client_obj in model_objs['clients']:
        client_obj.salesperson_id = random.choice(model_ids['salespeople'])
        db.session.add(client_obj)
    db.session.commit()

    # Generates a set of rows in sales_records for every book.
    for book_obj in model_objs['books']:
        start_date = date.fromisoformat(str(book_obj.publication_date))
        # If the book has is_in_print == True, generates records up to the
        # current month. Otherwise, picks a random "went out of print" date and
        # generates up to that point.
        end_date = date.today() if book_obj.is_in_print else generate_random_date(start_date)
        sales_records_objs = generate_sales_record_objs(book_obj.book_id, start_date, end_date)
        commit_model_objs_get_ids('sales_records', sales_records_objs)


# Iterates down the table_names list, deleting all rows from each table.
def delete_from_tables(db):
    # Delete all rows from database tables
    for table_name in table_names:
        db.session.execute(f'DELETE FROM {table_name};')
    db.session.commit()


# Reads a tsv file of testing data for the given table, forms an argd from each
# line, instances an object from the given class from each argd, and returns a
# list of the arguments.
def read_file_get_model_objs(table_name):
    model_class = table_to_model_class[table_name]
    file_path = os.path.join(data_dir, table_name + '.tsv')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'unable to locate file {file_path}')
    tsv_reader = csv.reader(open(file_path, 'r'), quotechar='"', delimiter='\t', skipinitialspace=True,
                                                  lineterminator='\n', quoting=csv.QUOTE_MINIMAL, doublequote=True)
    columns = next(tsv_reader)
    for row in tsv_reader:
        model_args = dict(zip(columns, row))
        if 'is_in_print' in model_args:
            model_args['is_in_print'] = True if model_args['is_in_print'] == 'True' else False
        model_objs.append(model_class(**model_args))
    return model_objs


# Commits the given SQLAlchemy.Model subclass objects to the db object, collects
# the values for their primary key, and returns the ids as a list.
def commit_model_objs_get_ids(table_name, model_objs):
    for model_obj in model_objs:
        db.session.add(model_obj)
    db.session.commit()
    id_column = table_to_model_class[table_name].__primary_key__
    return [getattr(model_obj, id_column) for model_obj in model_objs]


# Calculates the days elapsed between the date object argument and today,
# generates a random value between 1 and that value, then adds it to the date
# arguments using datetime.timedelta and returns the new date object.
def generate_random_date(lowerb_date):
    upperb_date = date.today()
    days_diff = (upperb_date - lowerb_date).days
    rand_day = random.randint(1, days_diff)
    return lowerb_date + timedelta(days=rand_day)


# Generates sales records for a given book_id, between the given start date and
# end date. A row is generated for each valid year-month pair between the two
# dates, inclusive.
def generate_sales_record_objs(book_id, start_date, end_date):
    sales_record_objs = list()
    profit_margin = random.uniform(0.075, 0.125)
    for year in range(start_date.year, end_date.year + 1):
        # Starts at the month of the start date if the year is the starting
        # year, else at 1. Ends at the month of the end date if the year is the
        # ending year, else at 13.
        for month in range(start_date.month if year == start_date.year else 1,
                           end_date.month + 1 if year == end_date.year else 13):
            # Picks a random number sold from a normal distribution.
            copies_sold = round(random.gauss(87.5, 20))
            gross_profit = copies_sold_to_gross_profit(copies_sold)
            net_profit = round(gross_profit*profit_margin, 2)
            # The arguments for a SalesRecord object.
            sales_record_args = dict(book_id=book_id, year=year, month=month, copies_sold=copies_sold,
                                     gross_profit=gross_profit, net_profit=net_profit)
            sales_record_obj = SalesRecord(**sales_record_args)
            sales_record_objs.append(sales_record_obj)
    return sales_record_objs


# Generates a random price paid for each copy sold and sums them.
def copies_sold_to_gross_profit(copies_sold):
    gross_profit = 0
    i = 0
    while i < copies_sold:
        single_sale_profit = round(random.gauss(12.5, 5), 2)
        if single_sale_profit <= 0:
            continue
        gross_profit += single_sale_profit
        i += 1
    return round(gross_profit, 2)


if __name__ == '__main__':
    main()
