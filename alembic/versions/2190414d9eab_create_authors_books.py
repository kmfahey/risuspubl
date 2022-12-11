"""create authors_books

Revision ID: 2190414d9eab
Revises: c792fc2930ad
Create Date: 2022-12-10 18:26:41.581634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2190414d9eab'
down_revision = 'c792fc2930ad'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE authors_books (
    author_id INT NOT NULL,
    book_id INT NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE authors_books;
""")
