## Risus Publishing

This project is an exercise in authoring a RESTful PostgreSQL db API using
`flask`, `SQLAlchemy` and `alembic`. The exercise's conceit is that the database
serves as the publishers/authors/editors-level database for a hypothetical
publishing company, Risus Publishing. Included in the `ansible` directory are
ansible script and data files to set up or tear down the database, and in the
`alembic` directory migrations to instantiate the database (which are used by
`ansible`).

The RESTful JSON API is implemented via the modules in `risuspubl.api.*`.
It's implemented by way of `flask` and `SQLAlchemy`. Executing `flask run` in
the top-level directory will spawn a `flask` web-server that will furnish the
endpoints under https://localhost:5000/. The `SQLAlchemy.Model` subclasses are
defined in `risuspubl.dbmodels` and the `create_app()` function that `flask`
depends on is defined in `risuspubl.api.flaskapp`.

### The Database

The default database name is `risuspubl`. The database's tables are:

* `authors`
    * the authors employed by the publishing company
* `authors_books`
    * a bridge table between `authors` and `books`
    * foreign keys `authors::author_id` and `books::book_id`
* `authors_manuscripts`
    * a bridge table between `authors` and `manuscripts`
    * foreign keys `authors::author_id` and `manuscripts::manuscript_id`
* `authors_metadata`
    * biographical information about the authors
    * foreign key `authors::author_id`: the author the info is about
* `books`
    * the books the publishing company has published
    * foreign key `editors::editor_id`: the editor who edited the book
    * foreign key `series::series_id`: the series the book belongs to (optional)
* `clients`
    * the publishing company's customers
    * foreign key `salespeople::salesperson_id`: the salesperson who manages
      the relationship with that client
* `editors`
    * the editors employed by the publishing company
* `manuscripts`
    * manuscripts currently in-progress by authors employed by the publishing company
    * foreign key `editors::editor_id`: the editor that is editing the manuscript
    * foreign key `series::series_id`: the series the manuscript belongs to (optional)
* `salespeople`
    * salespeople who work for the publishing company
* `sales_records`
    * by-month sales records for each book published by the company, from the
      date of publication to today (if it's still in print), or the date the
      book went out of print (otherwise)
    * foreign key `books::book_id`: the book that the sales record is for
* `series`
    * the series that some of the books and manuscripts can be grouped into

### The API

<table border=3 cellpadding=5 cellspacing=5>
    <tr>
        <th>HTTP<br>Method</th>
        <th>Endpoint URL, with embedded argument(s)</th>
        <th>Functionality</th>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/</nobr></code></td>
        <td>
            <p>
                Displays a help file in JSON format, listing each section of the
                app, every endpoint in each section, every method each endpoint accepts,
                and what functionality is offered by each method + endpoint combination.
                <code>authors</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>authors</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>authors</code> table
                associated with the given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors/{author_id}/books</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>books</code> table associated with the author with
                the given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors/{author_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>books</code>
                table associated with the given <code>book_id</code> and
                the given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors/{author_id}/manuscripts</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>manuscripts</code> table associated with the given
                <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/authors/{author_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>manuscripts</code> table associated with
                the given <code>manuscript_id</code> and the given
                <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/metadata
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object of the row in the
                <code>authors_metadata</code> table associated with the given
                <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for each of the two rows in the
                <code>authors</code> table associated with the two given
                <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/books
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>books</code> table associated with both the given
                <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>books</code>
                table associated with the given <code>book_id</code> and
                both the given <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/manuscripts
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>manuscripts</code> table associated with both the given
                <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>manuscripts</code> table associated with the
                given <code>manuscript_id</code> and both the two given
                <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>authors</code> table associated with the given
                <code>author_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>{ "first_name":&#160;"", "last_name":&#160;"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>books</code> table associated with the given
                <code>book_id</code> and the given <code>author_id</code>. The
                object has this form:
            </p>
            <blockquote>
                <code>
                    { "edition_number":&#160;, "editor_id":&#160;0,
                    "is_in_print":&#160;true,
                    "publication_date":&#160;"YYYY-MM-DD",
                    "series_id":&#160;null, "title":&#160;"" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>manuscripts</code> table associated with
                the given <code>manuscript_id</code> and the given
                <code>author_id</code>.  The object has this form:
            </p>
            <blockquote>
                <code>
                    { "advance":&#160;", "due_date":&#160;"",
                    "editor_id":&#160;0, "manuscript_id":&#160;0,
                    "series_id":&#160;null, "working_title":&#160;"" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/metadata
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>authors_metadata</code> table associated with
                the given <code>manuscript_id</code> and the given
                <code>author_id</code>.  The object has this form:
            </p>
            <blockquote>
                <code>
                    { author_id":&#160;0, "age":&#160;0, "biography":&#160;"",
                    "photo_url":&#160;"", "photo_res_horiz":&#160;0,
                    "photo_res_vert":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>books</code> table associated with the given
                <code>book_id</code> and the two given <code>author_id</code>
                values. The object has this form:
            </p>
            <blockquote>
                <code>
                    { edition_number":&#160;0, "editor_id":&#160;0,
                    "is_in_print":&#160;true,
                    "publication_date":&#160;"YYYY-MM-DD",
                    "series_id":&#160;null, "title":&#160;"" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>manuscripts</code> table associated with the
                given <code>manuscript_id</code> and the two given
                <code>author_id</code> values. The object has this form:
            </p>
            <blockquote>
                <code>
                    { advance":&#160;"", "due_date":&#160;"",
                    "editor_id":&#160;0, "manuscript_id":&#160;0,
                    "series_id":&#160;null, "working_title":&#160;"" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top><code><nobr>/authors</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to add a row in the <code>authors</code>
                table. The object has this form:
            </p>
            <blockquote>
                <code>{ "first_name":&#160;"", "last_name":&#160;"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/books
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the <code>books</code>
                table, and a row in the <code>authors_books</code> table
                associating it with the given <code>author_id</code>. The
                object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "series_id":&#160;null,
                    "title":&#160;"", "publication_date":&#160;"",
                    "edition_number":&#160;0, "is_in_print": "" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/manuscripts
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>manuscripts</code> table, and a row in the
                <code>authors_manuscripts</code> table associating it with
                the given <code>author_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "working_title":&#160;"", "due_date":
                    "YYYY-MM-DD", "advance":&#160;0 }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/metadata
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>authors_metadata</code> table associated with the
                given <code>author_id</code>. Fails if there already is
                a row in the <code>authors_metadata</code> table for that
                <code>author_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "author_id":&#160;0, "age":&#160;0, "biography":&#160;"",
                    "photo_url": "", "photo_res_horiz":&#160;0,
                    "photo_res_vert":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/books
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the <code>books</code>
                table and two rows in the <code>authors_books</code> table
                associating that row with both the given <code>author_id</code>
                values. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "series_id":&#160;null,
                    "title":&#160;"", "publication_date":&#160;"",
                    "edition_number":&#160;0, "is_in_print":
                    "" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/manuscripts
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>manuscripts</code> table and two rows in the
                <code>authors_manuscripts</code> table associating that row
                with both the given <code>author_id</code> values. The object
                has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "working_title":&#160;"",
                    "due_date":&#160;"YYYY-MM-DD", "advance":&#160;0,
                    "series_id":&#160;null }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>
                Deletes the row in the <code>authors</code> table associated
                with the given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>books</code> table associated
                with the given <code>book_id</code> and the given
                <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>manuscripts</code> table
                associated with the given <code>manuscript_id</code> and the
                given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author_id}/metadata
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>authors_metadata</code> table
                associated with the given <code>author_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>books</code> table associated
                with the given <code>book_id</code> and both the given
                <code>author_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>manuscripts</code> table
                associated with the given <code>manuscript_id</code>
                and both the given <code>author_id</code> values.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/books</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>books</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>books</code>
                table associated with the given <code>book_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>books</code> table associated with the given
                <code>book_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "series_id":&#160;0,
                    "title":&#160;"", publication_date":&#160;"YYYY-MM-DD",
                    "edition_number":&#160;0, "is_in_print":&#160;"" }
                </code>
            </blockquote>
            <p>
                The <code>series_id</code> argument is optional.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>
                Deletes the row in the <code>books</code> table associated with
                the given <code>book_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/clients</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>clients</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>clients</code>
                table associated with the given <code>client_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>clients</code> table associated with the given
                <code>client_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "email_address":&#160;"", "phone_number":&#160;"",
                    "business_name": "", "street_address":&#160;"",
                    "city":&#160;"", "state":&#160;"", "zipcode":&#160;"",
                    "country":&#160;"", "salesperson_id":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top><code><nobr>/clients</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to add a row in the <code>authors</code>
                table. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "salesperson_id":&#160;0, "email_address":&#160;"",
                    "phone_number": "", "business_name":&#160;"",
                    "street_address":&#160;"", "city":&#160;"",
                    "state":&#160;"", "zipcode":&#160;"", "country":&#160;"" }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>
                Deletes the row in the <code>clients</code> table associated
                with the given <code>client_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/editors</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>editors</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>editors</code>
                table associated with the given <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/editors/{editor_id}/books</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>books</code> table associated with the editor with
                the given <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>books</code>
                table associated with the given <code>book_id</code> and the
                given <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/manuscripts
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>manuscripts</code> table associated with <both the given
                code>editor_id</code> values.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>manuscripts</code> table associated with the given
                <code>manuscript_id</code> and the given <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>editors</code> table associated with the given
                <code>editor_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "first_name":&#160;"", "last_name":&#160;"",
                    "salary":&#160;0
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>books</code> table associated with the given
                <code>book_id</code> and the given <code>editor_id</code>. The
                object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, series_id":&#160;0,
                    "title":&#160;"", "publication_date":&#160;"YYYY-MM-DD",
                    "edition_number":&#160;0, "is_in_print":&#160;"" }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>manuscripts</code> table associated with
                the given <code>manuscript_id</code> and the given
                <code>editor_id</code>.  The object has this form:
            </p>
            <blockquote>
                <code>
                    { series_id":&#160;0, "working_title":&#160;"", "due_date":
                    "YYYY-MM-DD", "advance":&#160;0 }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top><code><nobr>/editors</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>editors</code> table. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "first_name":&#160;"", "last_name":&#160;"",
                    "salary":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>
                Deletes the row in the <code>editors</code> table associated
                with the given <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>books</code> table associated
                with the given <code>book_id</code> and the given
                <code>editor_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /editors/{editor_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>manuscripts</code> table
                associated with the given <code>manuscript_id</code>
                and the given <code>editor_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/manuscripts</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>manuscripts</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>manuscripts</code> table associated with the given
                <code>manuscript_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>manuscripts</code> table associated with the given
                <code>manuscript_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "editor_id":&#160;0, "series_id":&#160;0,
                    "working_title":&#160;"", "due_date":&#160;"YYYY-MM-DD",
                    "advance":&#160;0 }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>manuscripts</code> table
                associated with the given <code>manuscript_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/salespeople</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>salespeople</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>salespeople</code> table associated with the given
                <code>salesperson_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}/clients
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>clients</code> table associated with the salesperson
                with the given <code>salesperson_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}/clients/{client_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>clients</code> table associated with the given
                <code>client_id</code> and the given
                <code>salesperson_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>salespeople</code> table associated with the given
                <code>salesperson_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "first_name":&#160;"", "last_name":&#160;"",
                    "salary":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}/clients/{client_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>clients</code> table associated with the
                given <code>client_id</code> and the given
                <code>salesperson_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>
                    { email_address":&#160;"", "phone_number":&#160;"",
                    "business_name": "", "street_address":&#160;"",
                    "city":&#160;"", "state":&#160;"", "zipcode":&#160;"",
                    "country":&#160;"" }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top><code><nobr>/salespeople</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>salespeople</code> table. The object has this form:
            </p>
            <blockquote>
                <code>
                    { "first_name":&#160;"", "last_name":&#160;"", "salary":&#160;0 }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}/clients
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to add a row in the
                <code>clients</code> table, and a row in the
                <code>salespeople_clients</code> table associating it
                with the given <code>salesperson_id</code>. The object
                has this form:
            </p>
            <blockquote>
                <code>
                    { "email_address":&#160;"", "phone_number":&#160;"",
                    "business_name": "", "street_address":&#160;"",
                    "city":&#160;"", "state":&#160;"", "zipcode":&#160;"",
                    "country":&#160;"" }
                </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>salespeople</code> table
                associated with the given <code>salesperson_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>DELETE</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /salespeople/{salesperson_id}/clients/{client_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Deletes the row in the <code>clients</code> table associated
                with the given <code>client_id</code> and the given
                <code>salesperson_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /sales_records/{sales_record_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>sales_records</code> table associated with the given
                <code>sales_record_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/sales_records/year/{year}</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>sales_records</code> table associated with the given
                <code>year</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /sales_records/year/{year}/month/{month}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>sales_records</code> table associated with the given
                <code>year</code> and <code>month</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /sales_records/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>sales_records</code> table associated with the given
                <code>book_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /sales_records/year/{year}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>sales_records</code> table associated with the given
                <code>year</code> and <code>book_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /sales_records/year/{year}/month/{month}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>sales_records</code> table associated with the given
                <code>year</code>, <code>month</code> and <code>book_id</code>.
            </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/series</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for every row in the
                <code>series</code> table.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>series</code>
                table associated with the given <code>series_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top><code><nobr>/series/{series_id}/books</nobr></code></td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>books</code> table associated with the salesperson with
                the given <code>series_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /series/{series_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the <code>books</code>
                table associated with the given <code>book_id</code> and the
                given <code>series_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /series/{series_id}/manuscripts
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON list of objects, one for each row in the
                <code>manuscripts</code> table associated with the salesperson
                with the given <code>series_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>GET</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /series/{series_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Displays a JSON object for the row in the
                <code>manuscripts</code> table associated with
                the given <code>manuscript_id</code> and the given
                <code>series_id</code>.
            </p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>series</code> table associated with the given
                <code>series_id</code>. The object has this form:
            </p>
            <blockquote>
                <code>{ "title":&#160;"", "volumes":&#160;0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /series/{series_id}/books/{book_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>books</code> table associated with the given
                <code>book_id</code> and the given <code>series_id</code>. The
                object has this form:
            </p>
            <blockquote>
                <code>
                    { "title":&#160;"", publication_date":&#160;"YYYY-MM-DD",
                    "edition_number":&#160;1, "is_in_print":&#160;true }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>PATCH</code></td>
        <td valign=top>
            <code>
                <nobr>
                    /series/{series_id}/manuscripts/{manuscript_id}
                </nobr>
            </code>
        </td>
        <td>
            <p>
                Accepts a JSON object to modify the row in the
                <code>manuscripts</code> table associated with the given
                <code>manuscript_id</code> and the given <code>series_id</code>.
                The object has this form:
            </p>
            <blockquote>
                <code>
                    { "title":&#160;"", publication_date":&#160;"YYYY-MM-DD",
                    "edition_number":&#160;1, "is_in_print":&#160;true }
                </code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td valign=top><code>POST</code></td>
        <td valign=top><code><nobr>/series</nobr></code></td>
        <td>
            <p>
                Accepts a JSON object to add a row in the <code>series</code>
                table. The object has this form:
            </p>
            <blockquote>
                <code>{ "title":&#160;"", "volumes":&#160;0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td valign=top><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>
                Deletes the row in the <code>series</code> table
                associated with the given <code>series_id</code>.
            </p>
        </td>
    </tr>
</table>
