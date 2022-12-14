"""alter authors_metadata add fk author_id

Revision ID: 4b68d8d52ad1
Revises: fb0694e5e019
Create Date: 2022-12-11 13:37:14.252451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b68d8d52ad1'
down_revision = 'fb0694e5e019'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE authors_metadata
ADD CONSTRAINT fk_authors
FOREIGN KEY (author_id)
REFERENCES authors (author_id)
ON DELETE SET NULL;
""")


def downgrade():
    op.execute("""
ALTER TABLE authors_metadata
DROP CONSTRAINT fk_authors;
""")
