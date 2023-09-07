"""alter authors_books add fk book_id

Revision ID: fb44c130a2cc
Revises: c46e7d48060e
Create Date: 2022-12-10 18:38:09.277436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb44c130a2cc"
down_revision = "c46e7d48060e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE authors_books
ADD CONSTRAINT fk_books
FOREIGN KEY (book_id)
REFERENCES books (book_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE authors_books
DROP CONSTRAINT fk_books;
"""
    )
