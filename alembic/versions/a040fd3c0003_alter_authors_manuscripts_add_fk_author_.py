"""alter authors_manuscripts add fk author_id

Revision ID: a040fd3c0003
Revises: fb44c130a2cc
Create Date: 2022-12-10 18:39:16.597975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a040fd3c0003"
down_revision = "fb44c130a2cc"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE authors_manuscripts
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE authors_manuscripts
DROP CONSTRAINT fk_authors;
"""
    )
