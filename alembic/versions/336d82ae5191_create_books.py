"""create books

Revision ID: 336d82ae5191
Revises: 388dfda0ace7
Create Date: 2022-12-10 18:28:26.863665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '336d82ae5191'
down_revision = '388dfda0ace7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    editor_id INT NOT NULL,
    series_id INT,
    title VARCHAR(64) UNIQUE NOT NULL,
    publication_date DATE NOT NULL,
    edition_number INT NOT NULL,
    is_in_print BOOLEAN NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE books;
""")
