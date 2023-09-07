"""alter authors_books add fk author_id

Revision ID: c46e7d48060e
Revises: 670c8486947d
Create Date: 2022-12-10 18:35:23.874286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c46e7d48060e"
down_revision = "670c8486947d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE authors_books
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE authors_books
DROP CONSTRAINT fk_authors;
"""
    )
