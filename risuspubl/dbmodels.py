#!/usr/bin/python3

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    __primary_key__ = 'author_id'

    author_id = db.Column('author_id', db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column('first_name', db.String(64), nullable=False)
    last_name = db.Column('last_name', db.String(64), nullable=False)

    def serialize(self):
        return {
            'author_id': self.author_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            }


class Book(db.Model):
    __tablename__ = 'books'
    __primary_key__ = 'book_id'

    book_id = db.Column('book_id', db.Integer, primary_key=True, autoincrement=True)
    # These can't be defined now because the Editor and Series classes don't
    # exist yet. They're assigned later once the Editor and Series classes have
    # been defined.
    # editor_id = db.Column('editor_id', db.ForeignKey(Editor.editor_id), nullable=False)
    # series_id = db.Column('series_id', db.ForeignKey(Series.series_id), nullable=True)
    title = db.Column('title', db.String(64), nullable=False)
    publication_date = db.Column('publication_date', db.Date, nullable=False)
    edition_number = db.Column('edition_number', db.Integer, nullable=False)
    is_in_print = db.Column('is_in_print', db.Boolean, nullable=False)

    def serialize(self):
        return {
            'book_id': self.book_id,
            'editor_id': self.editor_id,
            'series_id': self.series_id,
            'title': self.title,
            'publication_date': str(self.publication_date),
            'edition_number': self.edition_number,
            'is_in_print': self.is_in_print,
            }


class Client(db.Model):
    __tablename__ = 'clients'
    __primary_key__ = 'client_id'

    client_id = db.Column('client_id', db.Integer, primary_key=True, autoincrement=True)
    # This can't be defined now because the Salesperson table doesn't exist yet.
    # It's assigned later once Salesperson has been defined.
    # salesperson_id = db.Column('salesperson_id', db.ForeignKey(Salesperson.salesperson_id), nullable=False)
    email_address = db.Column('email_address', db.String(64), nullable=True)
    phone_number = db.Column('phone_number', db.String(11), nullable=False)
    business_name = db.Column('business_name', db.String(64), nullable=False)
    street_address = db.Column('street_address', db.String(64), nullable=False)
    city = db.Column('city', db.String(64), nullable=False)
    state = db.Column('state', db.String(2), nullable=False)
    zipcode = db.Column('zipcode', db.String(9), nullable=False)
    country = db.Column('country', db.String(64), nullable=False)

    def serialize(self):
        return {
            'client_id': self.client_id,
            'salesperson_id': self.salesperson_id,
            'email_address': self.email_address,
            'phone_number': self.phone_number,
            'business_name': self.business_name,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'country': self.country,
            }


class Editor(db.Model):
    __tablename__ = 'editors'
    __primary_key__ = 'editor_id'

    editor_id = db.Column('editor_id', db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column('first_name', db.String(64), nullable=False)
    last_name = db.Column('last_name', db.String(64), nullable=False)
    salary = db.Column('salary', db.Integer, nullable=False)

    def serialize(self):
        return {
            'editor_id': self.editor_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'salary': self.salary,
            }


# Defining these late because the 2nd Model subclass didn't exist until now.
Book.editor_id = db.Column('editor_id', db.ForeignKey(Editor.editor_id), nullable=False)


class Manuscript(db.Model):
    __tablename__ = 'manuscripts'
    __primary_key__ = 'manuscript_id'

    manuscript_id = db.Column('manuscript_id', db.Integer, primary_key=True, autoincrement=True)
    editor_id = db.Column('editor_id', db.ForeignKey(Editor.editor_id), nullable=False)
    # This can't be defined now because the Series table doesn't exist yet. It's
    # assigned later once Series has been defined.
    # series_id = db.Column('series_id', db.ForeignKey(Series.series_id), nullable=False)
    working_title = db.Column('working_title', db.String(64), nullable=False)
    due_date = db.Column('due_date', db.Date, nullable=False)
    advance = db.Column('advance', db.Integer, nullable=False)

    def serialize(self):
        return {
            'manuscript_id': self.manuscript_id,
            'editor_id': self.editor_id,
            'series_id': self.series_id,
            'working_title': self.working_title,
            'due_date': str(self.due_date),
            'advance': self.advance,
            }


class SalesRecord(db.Model):
    __tablename__ = 'sales_records'
    __primary_key__ = 'sales_record_id'

    sales_record_id = db.Column('sales_record_id', db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column('book_id', db.Integer, nullable=False)
    year = db.Column('year', db.Integer, nullable=False)
    month = db.Column('month', db.Integer, nullable=False)
    copies_sold = db.Column('copies_sold', db.Numeric, nullable=False)
    gross_profit = db.Column('gross_profit', db.Numeric, nullable=False)
    net_profit = db.Column('net_profit', db.Integer, nullable=False)

    def serialize(self):
        return {
            'sales_record_id': self.sales_record_id,
            'book_id': self.book_id,
            'year': self.year,
            'month': self.month,
            'copies_sold': self.copies_sold,
            'gross_profit': self.gross_profit,
            'net_profit': self.net_profit,
            }


class Salesperson(db.Model):
    __tablename__ = 'salespeople'
    __primary_key__ = 'salesperson_id'

    salesperson_id = db.Column('salesperson_id', db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column('first_name', db.String(64), nullable=False)
    last_name = db.Column('last_name', db.String(64), nullable=False)
    salary = db.Column('salary', db.Integer, nullable=False)

    def serialize(self):
        return {
            'salesperson_id': self.salesperson_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'salary': self.salary,
            }


# Defining these late because the 2nd Model subclass didn't exist until now.
Client.salesperson_id = db.Column('salesperson_id', db.ForeignKey(Salesperson.salesperson_id), nullable=False)


class Series(db.Model):
    __tablename__ = 'series'
    __primary_key__ = 'series_id'

    series_id = db.Column('series_id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(64), nullable=False)
    volumes = db.Column('volumes', db.Integer, nullable=False)

    def serialize(self):
        return {
            'series_id': self.series_id,
            'title': self.title,
            'volumes': self.volumes,
            }


# Defining these late because the 2nd Model subclass didn't exist until now.
Book.series_id = db.Column('series_id', db.ForeignKey(Series.series_id), nullable=True)

Manuscript.series_id = db.Column('series_id', db.ForeignKey(Series.series_id), nullable=False)


# Defining a Table subclass object that represents the authors_books table, and
# assigning attributes to the Book and Author classes such that an Author object
# will have a books attribute containing a list of Book objects whose book_ids
# are associated in the authors_books table with the given author_id, and vice
# versa for Book objects.
Authors_Books = db.Table('authors_books',
                         db.Column('author_id', db.ForeignKey(Author.author_id), primary_key=True, autoincrement=False),
                         db.Column('book_id', db.ForeignKey(Book.book_id), primary_key=True, autoincrement=False)
                         )

Author.books = db.relationship('Book', secondary=Authors_Books, lazy='subquery', viewonly=True,
                               backref=db.backref('author_books', lazy=True))
Book.authors = db.relationship('Author', secondary=Authors_Books, lazy='subquery', viewonly=True,
                               backref=db.backref('book_authors', lazy=True))


# Defining a Table subclass object that represents the authors_manuscripts
# table, and assigning attributes to the Manuscript and Author classes
# such that an Author object will have a manuscripts attribute containing
# a list of Manuscript objects whose manuscript_ids are associated in the
# authors_manuscripts table with the given author_id, and vice versa for
# Manuscript objects.
Authors_Manuscripts = db.Table('authors_manuscripts',
                               db.Column('author_id', db.ForeignKey(Author.author_id), primary_key=True,
                                         autoincrement=False),
                               db.Column('manuscript_id', db.ForeignKey(Manuscript.manuscript_id), primary_key=True,
                                         autoincrement=False)
                               )

Manuscript.authors = db.relationship('Author', secondary=Authors_Manuscripts, lazy='subquery', viewonly=True,
                                     backref=db.backref('manuscript_authors', lazy=True))
Author.manuscripts = db.relationship('Manuscript', secondary=Authors_Manuscripts, lazy='subquery', viewonly=True,
                                     backref=db.backref('author_manuscripts', lazy=True))
