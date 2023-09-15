#!/usr/bin/python3

import decouple
import psycopg2
import sys

from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


if len(sys.argv) != 2:
    print("Usage: setup_db.py <POSTGRES_PASSWORD>")
    sys.exit(1)

postgres_user = "postgres"
postgres_password = sys.argv[1]
postgres_db = "template1"

DB_USER = decouple.config("DB_USER")
DB_PASSWORD = decouple.config("DB_PASSWORD")
DB_HOST = decouple.config('DB_HOST')
DB_PORT = decouple.config('DB_PORT')
DB_NAME = decouple.config("DB_NAME")

# Connect to PostgreSQL with the default user, usually 'postgres'
conn = psycopg2.connect(
    user=postgres_user, password=postgres_password, host=DB_HOST, port=DB_PORT, dbname=postgres_db
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Create the user if it doesn't exist
cursor.execute(
    sql.SQL(
        """\
DO $$
BEGIN
    CREATE ROLE {user} WITH LOGIN PASSWORD {password};
EXCEPTION
    WHEN duplicate_object THEN
        -- nothing
END $$;
        """
    ).format(user=sql.Identifier(DB_USER), password=sql.SQL("'%s'" % DB_PASSWORD))
)

# Create the database.
cursor.execute(sql.SQL("CREATE DATABASE {db};").format(db=sql.Identifier(DB_NAME)))

# Grant all privileges to the user
cursor.execute(
    sql.SQL(
        """\
GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};
GRANT ALL ON ALL TABLES IN SCHEMA public TO {user};
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {user};
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO {user};
    """
    ).format(db=sql.Identifier(DB_NAME), user=sql.Identifier(DB_USER))
)

cursor.close()
conn.close()
