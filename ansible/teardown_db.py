#!/usr/bin/python3

import decouple
import psycopg2
import sys

from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


if len(sys.argv) != 2:
    print("Usage: teardown_db.py <POSTGRES_PASSWORD>")
    sys.exit(1)

postgres_user = "postgres"
postgres_password = sys.argv[1]
postgres_db = "template1"

DB_USER = decouple.config("DB_USER")
DB_HOST = decouple.config('DB_HOST')
DB_PORT = decouple.config('DB_PORT')
DB_NAME = decouple.config("DB_NAME")
TESTING_DB_NAME = decouple.config("TESTING_DB_NAME")

conn = psycopg2.connect(
    user=postgres_user, password=postgres_password, host=DB_HOST, port=DB_PORT, dbname=postgres_db
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Drop the database
cursor.execute(sql.SQL("DROP DATABASE {db};").format(db=sql.Identifier(DB_NAME)))
cursor.execute(sql.SQL("DROP DATABASE {db};").format(db=sql.Identifier(TESTING_DB_NAME)))

# Drop the user
cursor.execute(sql.SQL("DROP USER {user};").format(user=sql.Identifier(DB_USER)))
