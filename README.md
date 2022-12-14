## Risus Publishing Database

An exercise in authoring a RESTful psql db API using flask, SQLAlchemy and alembic, completed as part of NuCamp's devops coding bootcamp. The conceit is that the database serves as the publishers/authors/editors-level database for a publishing company, Risus Publishing.

Included are the alembic migrations needed to instantiate the database in [./alembic/](./alembic/), a [./load\_testing\_data.py](./load_testing_data.py) script to populate or repopulate the database with testing data, and the testing data .tsv files in [./data/](./data/).

The RESTful JSON API is implemented via the modules in [./risuspubl/api/](./risuspubl/api/). It's implemented by way of `flask` and `SQLAlchemy`; executing `flask run` in the toplevel directory will spawn a `flask` webserver that will furnish the endpoints at https://localhost:5000/.

(See the [Portfolio Project Requirements Checklist](./Portfolio_Project_Requirements_Checklist.html) for a detailed review of the checklist from [the Portfolio Project Final Submission page](https://learn.nucamp.co/mod/forum/view.php?id=5133) with indications where files satisfying each requirement can be found.)

#### The Project


#### The Tables

The default database name is `risuspublishing`. The database's tables are:

* `authors`
    * the authors employed by the publishing company
* `author_books`
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
    * foreign key `salespeople::salesperson_id`: the salesperson who manages the relationship with that client
* `editors`
    * the editors employed by the publishing company
* `manuscripts`
    * manuscripts currently in-progress by authors employed by the publishing company
    * foreign key `editors::editor_id`: the editor that is editing the manuscript
    * foreign key `series::series_id`: the series the manuscript belongs to (optional)
* `salespeople`
    * salespeople who work for the publishing company
* `sales_records`
    * by-month sales records for each book published by the company, from the date of publication to today (if it's still in print), or the date the book went out of print (otherwise)
    * foreign key `books::book_id`: the book that the the sales record is for
* `series`
    * the series that some of the books and manuscripts can be grouped into

#### The API

<table border=3 cellpadding=5 cellspacing=5>
    <tr>
        <th>HTTP<br>Method</th>
        <th>endpoint URL with embedded id(s)</th>
        <th>functionality</th>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>authors</code> table.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>authors</code> table associated with the given
            <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}/books</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for every row in the <code>books</code> table associated with the
            author with the given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>books</code> table associated with the given
            <code>book_id</code> and the given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}/manuscripts</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for every row in the <code>manuscripts</code> table associated with
            <the given code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author_id}/metadata</nobr></code></td>
        <td>
            <p>Displays a JSON object of the row in the <code>authors_metadata</code> table associated with the given
            <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for each of the two rows in the <code>authors</code> table associated with the two
            given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/books</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>books</code> table associated with both
            the given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>books</code> table associated with the given
            <code>book_id</code> and both the given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/manuscripts</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>manuscripts</code> table associated with
            both the given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and both the two given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>authors</code> table associated with the given
            <code>author_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>books</code> table associated with the
            given <code>book_id</code> and the given <code>author_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "edition_number":, "editor_id": 0, "is_in_print": true, "publication_date": "YYYY-MM-DD",
                "series_id": null, "title": "" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>manuscripts</code> table associated with the
            given <code>manuscript_id</code> and the given <code>author_id</code>. The object has this form:</p></p>
            <blockquote>
                <code>{ "advance":", "due_date": "", "editor_id": 0, "manuscript_id": 0, "series_id": null,
                "working_title": "" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author_id}/metadata</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>authors_metadata</code> table associated with
            the given <code>manuscript_id</code> and the given <code>author_id</code>. The object has this form:</p>
            <blockquote>
                <code>{author_id": 0, "age": 0, "biography": "", "photo_url": "", "photo_res_horiz": 0,
                "photo_res_vert": 0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>books</code> table associated with the
            given <code>book_id</code> and the two given <code>author_id</code> values. The object has this form:</p>
            <blockquote>
                <code>{edition_number": 0, "editor_id": 0, "is_in_print": true, "publication_date": "YYYY-MM-DD",
                "series_id": null, "title": "" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the two given <code>author_id</code> values. The object has this form:</p>
            <blockquote>
                <code>{advance": "", "due_date": "", "editor_id": 0, "manuscript_id": 0, "series_id": null,
                "working_title": "" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>authors</code> table. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors/{author_id}/books</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>books</code> table, and a row in the
            <code>authors_books</code> table associating it with the given <code>author_id</code>. The object hashe form
            <code>{ "editor_id":0, "series_id":null, "title":"", "publication_date":"", "edition_number":0,
            "is_in_print":"" }</code> The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors/{author_id}/manuscripts</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>manuscripts</code> table, and a row in the
            <code>authors_manuscripts</code> table associating it with the given <code>author_id</code>. The objectas
            the form <code>{ "editor_id":0, "working_title":"", "due_date":"YYYY-MM-DD", "advance":0 }</code> The
            <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors/{author_id}/metadata</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>authors_metadata</code> table associated with the given
            <code>author_id</code>. Fails if there already is a row in the <code>authors_metadata</code> table forhat
            <code>author_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "author_id": 0, "age": 0, "biography": "", "photo_url": "", "photo_res_horiz": 0,
                "photo_res_vert": 0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/books</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>books</code> table and two rows in the
            <code>authors_books</code> table associating that row with both the given <code>author_id</code> values.The
            object has this form:</p>
            <blockquote>
                <code>{ "editor_id":0, "series_id":null, "title":"", "publication_date":"", "edition_number":0,
                "is_in_print":"" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/manuscripts</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>manuscripts</code> table and two rows in the
            <code>authors_manuscripts</code> table associating that row with both the given <code>author_id</code>alues.
            The object has this form:</p>
            <blockquote>
                <code>{ "editor_id":0, "working_title":"", "due_date":"YYYY-MM-DD", "advance":0, "series_id":null
                }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>authors</code> table associated with the given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>books</code> table associated with the given <code>book_id</code> and the
            given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the given <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author_id}/metadata</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>authors_metadata</code> table associated with the given
            <code>author_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>books</code> table associated with the given <code>book_id</code> and both
            the given <code>author_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/authors/{author1_id}/{author2_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and both the given <code>author_id</code> values.</p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/books</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>books</code> table. </p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>books</code> table associated with the given
            <code>book_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>books</code> table associated with
            the given <code>book_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "editor_id":0, "series_id":0, "title":"",publication_date":"YYYY-MM-DD", "edition_number":0,
                "is_in_print":"" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/books/{book_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>books</code> table associated with the given <code>book_id</code>. </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/clients</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>clients</code> table. </p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>clients</code> table associated with the given
            <code>client_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>clients</code> table associated with the
            given <code>client_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "email_address":"", "phone_number":"", business_name":"", "street_address":"", "city":"",
                "state":"", "zipcode":"", "country":"", "salesperson_id":0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/clients</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>authors</code> table. The object has this form:</p>
            <blockquote>
                <code>{ "salesperson_id":0, "email_address":"", "phone_number":"", "business_name":"",
                "street_address":"",city":"", "state":"", "zipcode":"", "country":"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/clients/{client_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>clients</code> table associated with the given <code>client_id</code>.</p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>editors</code> table.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>editors</code> table associated with the given
            <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors/{editor_id}/books</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>books</code> table associated with the
            editor with the given <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors/{editor_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>books</code> table associated with the given
            <code>book_id</code> and the given <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors/{editor_id}/manuscripts</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>manuscripts</code> table associated with
            <both the given code>editor_id</code> values.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/editors/{editor_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the given <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>editors</code> table associated with the given
            <code>editor_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"", "salary":0</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/editors/{editor_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>books</code> table associated with the
            given <code>book_id</code> and the given <code>editor_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "editor_id":0,series_id":0, "title":"", "publication_date":"YYYY-MM-DD", "edition_number":0,
                "is_in_print":"" }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/editors/{editor_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>manuscripts</code> table associated with
            the given <code>manuscript_id</code> and the given <code>editor_id</code>. The object has the
            form <code>{series_id":0, "working_title":"", "due_date":"YYYY-MM-DD", "advance":0 }</code> The
            <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/editors</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>editors</code> table. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"", "salary":0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/editors/{editor_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>editors</code> table associated with the given <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/editors/{editor_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>books</code> table associated with the given <code>book_id</code> and the
            given <code>editor_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/editors/{editor_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the given <code>editor_id</code>.</p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/manuscripts</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>manuscripts</code> table. </p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "editor_id":0, "series_id":0,working_title":"", "due_date":"YYYY-MM-DD", "advance":0 }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code>. </p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/salespeople</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>salespeople</code> table. </p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>salespeople</code> table associated with the given
            <code>salesperson_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}/clients</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>clients</code> table associated with the
            salesperson with the given <code>salesperson_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}/clients/{client_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>clients</code> table associated with the given
            <code>client_id</code> and the given <code>salesperson_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>salespeople</code> table associated with the
            given <code>salesperson_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"", "salary":0</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}/clients/{client_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>clients</code> table associated with the
            given <code>client_id</code> and the given <code>salesperson_id</code>. The object has this form:</p>
            <blockquote>
                <code>{email_address":"", "phone_number":"", "business_name":"", "street_address":"", "city":"",
                "state":"", "zipcode":"", "country":"" }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/salespeople</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>salespeople</code> table. The object has this form:</p>
            <blockquote>
                <code>{ "first_name":"", "last_name":"", "salary":0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}/clients</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>clients</code> table, and a row in the
            <code>salespeople_clients</code> table associating it with the given <code>salesperson_id</code>. Thebject
            has this form:</p>
            <blockquote>
                <code>{ "email_address":"", "phone_number":"", "business_name":"", "street_address":"", "city":"",
                "state":"", "zipcode":"", "country":"" } </code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>salespeople</code> table associated with the given
            <code>salesperson_id</code>. </p>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/salespeople/{salesperson_id}/clients/{client_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>clients</code> table associated with the given <code>client_id</code> and
            the given <code>salesperson_id</code>.</p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/sales_records/{sales_record_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>sales_records</code> table associated with the given
            <code>sales_record_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/sales_records/year/{year}</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for every row in the <code>sales_records</code> table associated
            with the given <code>year</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/sales_records/year/{year}/month/{month}</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for every row in the <code>sales_records</code> table associated
            with the given <code>year</code> and <code>month</code>.</p>
        </td>
    </tr>

    <tr>
        <td colspan="3"><hr width="75%"></td>
    </tr>

    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for every row in the <code>series</code> table. </p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>series</code> table associated with the given
            <code>series_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series/{series_id}/books</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>books</code> table associated with the
            salesperson with the given <code>series_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series/{series_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>books</code> table associated with the given
            <code>book_id</code> and the given <code>series_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series/{series_id}/manuscripts</nobr></code></td>
        <td>
            <p>Displays a list of JSON objects, one for each row in the <code>manuscripts</code> table associated with
            the salesperson with the given <code>series_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>GET</code></td>
        <td><code><nobr>/series/{series_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Displays a JSON object for the row in the <code>manuscripts</code> table associated with the given
            <code>manuscript_id</code> and the given <code>series_id</code>.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>series</code> table associated with the given
            <code>series_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "title":"", "volumes":0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/series/{series_id}/books/{book_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>books</code> table associated with the
            given <code>book_id</code> and the given <code>series_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "title":"",publication_date":"YYYY-MM-DD", "edition_number":1, "is_in_print":true }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>PATCH</code></td>
        <td><code><nobr>/series/{series_id}/manuscripts/{manuscript_id}</nobr></code></td>
        <td>
            <p>Accepts a JSON object to modify the row in the <code>manuscripts</code> table associated with
            the given <code>manuscript_id</code> and the given <code>series_id</code>. The object has this form:</p>
            <blockquote>
                <code>{ "title":"",publication_date":"YYYY-MM-DD", "edition_number":1, "is_in_print":true }</code>
            </blockquote>
            <p>The <code>series_id</code> argument is optional.</p>
        </td>
    </tr>
    <tr>
        <td><code>POST</code></td>
        <td><code><nobr>/series</nobr></code></td>
        <td>
            <p>Accepts a JSON object to add a row in the <code>series</code> table. The object has this form:</p>
            <blockquote>
                <code>{ "title":"", "volumes":0 }</code>
            </blockquote>
        </td>
    </tr>
    <tr>
        <td><code>DELETE</code></td>
        <td><code><nobr>/series/{series_id}</nobr></code></td>
        <td>
            <p>Deletes the row in the <code>series</code> table associated with the given <code>series_id</code>.</p>
        </td>
    </tr>
</table>
