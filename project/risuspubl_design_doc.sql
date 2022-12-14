CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL
);

CREATE TABLE authors_books (
    author_id INT,
    book_id INT,
    PRIMARY KEY (author_id, book_id)
);

CREATE TABLE authors_manuscripts (
    author_id INT,
    manuscript_id INT,
    PRIMARY KEY (author_id, manuscript_id)
);

CREATE TABLE authors_metadata (
    author_metadata_id SERIAL PRIMARY KEY,
    author_id INT,
    age INT NOT NULL,
    biography TEXT NOT NULL,
    photo_url VARCHAR(256) NOT NULL,
    photo_res_horiz INT NOT NULL,
    photo_res_vert INT NOT NULL
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    editor_id INT,
    series_id INT,
    title VARCHAR(64) UNIQUE NOT NULL,
    publication_date DATE NOT NULL,
    edition_number INT NOT NULL,
    is_in_print BOOLEAN NOT NULL
);

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    salesperson_id INT,
    email_address VARCHAR(64) UNIQUE NOT NULL,
    phone_number VARCHAR(11) UNIQUE NOT NULL,
    business_name VARCHAR(64) UNIQUE NOT NULL,
    street_address VARCHAR(64) NOT NULL,
    city VARCHAR(64) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zipcode VARCHAR(9) NOT NULL,
    country VARCHAR(64) NOT NULL
);

CREATE TABLE editors (
    editor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    salary NUMERIC NOT NULL
);

CREATE TABLE manuscripts (
    manuscript_id SERIAL PRIMARY KEY,
    editor_id INT,
    series_id INT,
    working_title VARCHAR(64) UNIQUE NOT NULL,
    due_date DATE NOT NULL,
    advance NUMERIC NOT NULL
);

CREATE TABLE salespeople (
    salesperson_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    salary NUMERIC NOT NULL
);

CREATE TABLE sales_records (
    sales_record_id SERIAL PRIMARY KEY,
    book_id INT,
    year INTEGER NOT NULL,
    month VARCHAR(64),
    copies_sold INTEGER,
    gross_profit NUMERIC,
    net_profit NUMERIC
);

CREATE TABLE series (
    series_id SERIAL PRIMARY KEY,
    title VARCHAR(64) UNIQUE NOT NULL,
    volumes INT NOT NULL
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

ALTER TABLE authors_metadata
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE SET NULL;

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

ALTER TABLE clients
ADD CONSTRAINT fk_salesperson
FOREIGN KEY (salesperson_id)
REFERENCES salespeople (salesperson_id)
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

ALTER TABLE sales_records
ADD CONSTRAINT fk_book
FOREIGN KEY (book_id)
REFERENCES books (book_id)
ON DELETE RESTRICT;

CREATE INDEX idx_authors_metadata_author_id ON authors_metadata USING hash(author_id);

CREATE INDEX idx_books_editor_id ON books USING hash(editor_id);

CREATE INDEX idx_books_series_id ON books USING hash(series_id);

CREATE INDEX idx_clients_salesperson_id ON clients USING hash(salesperson_id);

CREATE INDEX idx_manuscripts_editor_id ON manuscripts USING hash(editor_id);

CREATE INDEX idx_manuscripts_series_id ON manuscripts USING hash(series_id);

CREATE INDEX idx_sales_records_book_id ON sales_records USING hash(book_id);
