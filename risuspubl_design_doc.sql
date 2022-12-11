
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
);

CREATE TABLE authors_books (
    author_id INT NOT NULL,
    book_id INT NOT NULL
);

CREATE TABLE authors_manuscripts (
    author_id INT NOT NULL,
    manuscript_id INT NOT NULL
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    author_id INT NOT NULL,
    editor_id INT NOT NULL,
    series_id INT,
    title TEXT UNIQUE NOT NULL,
    publication_date DATE NOT NULL,
    edition_number INT NOT NULL,
    is_in_print BOOLEAN NOT NULL
);

CREATE TABLE manuscripts (
    manuscript_id SERIAL PRIMARY KEY,
    author_id INT NOT NULL,
    editor_id INT NOT NULL,
    series_id INT,
    working_title TEXT UNIQUE NOT NULL,
    due_date DATE NOT NULL,
    advance NUMERIC NOT NULL
);

CREATE TABLE series (
    series_id SERIAL PRIMARY KEY,
    title TEXT UNIQUE NOT NULL,
    volumes INT NOT NULL
);

CREATE TABLE editors (
    editor_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    salary NUMERIC NOT NULL
);

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    salesperson_id INT UNIQUE NOT NULL,
    email_address TEXT UNIQUE NOT NULL,
    phone_number INTEGER UNIQUE NOT NULL,
    business_name TEXT UNIQUE NOT NULL,
    street_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state_or_province TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE salespeople (
    salesperson_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    salary NUMERIC NOT NULL
);

CREATE TABLE sales_records (
    sales_record_id SERIAL PRIMARY KEY,
    book_id INT,
    client_id INT,
    year INTEGER NOT NULL,
    month TEXT ,
    copies_sold INTEGER,
    gross_profit NUMERIC,
    net_profit NUMERIC
);

ALTER TABLE authors_books
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;

ALTER TABLE authors_books
ADD CONSTRAINT fk_books
FOREIGN KEY (book_id)
REFERENCES books (book_id)
ON DELETE RESTRICT;

ALTER TABLE authors_manuscripts
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;

ALTER TABLE authors_manuscripts
ADD CONSTRAINT fk_manuscripts
FOREIGN KEY (manuscript_id)
REFERENCES manuscripts (manuscript_id)
ON DELETE RESTRICT;

ALTER TABLE books
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;

ALTER TABLE books
ADD CONSTRAINT fk_editors
FOREIGN KEY (editor_id)
REFERENCES editors (editor_id)
ON DELETE RESTRICT;

ALTER TABLE books
ADD CONSTRAINT fk_series
FOREIGN KEY (series_id)
REFERENCES series (series_id)
ON DELETE RESTRICT;

ALTER TABLE manuscripts
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;

ALTER TABLE manuscripts
ADD CONSTRAINT fk_editors
FOREIGN KEY (editor_id)
REFERENCES editors (editor_id)
ON DELETE RESTRICT;

ALTER TABLE manuscripts
ADD CONSTRAINT fk_series
FOREIGN KEY (series_id)
REFERENCES series (series_id)
ON DELETE RESTRICT;

ALTER TABLE clients
ADD CONSTRAINT fk_salesperson
FOREIGN KEY (salesperson_id)
REFERENCES salespeople (salesperson_id)
ON DELETE RESTRICT;

ALTER TABLE sales_records
ADD CONSTRAINT fk_book
FOREIGN KEY (book_id)
REFERENCES books (book_id)
ON DELETE RESTRICT;

ALTER TABLE sales_records
ADD CONSTRAINT fk_client
FOREIGN KEY (client_id)
REFERENCES clients (client_id)
ON DELETE RESTRICT;


