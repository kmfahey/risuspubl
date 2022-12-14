"""add index on authors_metadata hash author_id

Revision ID: ac8b8ff6849d
Revises: 4b68d8d52ad1
Create Date: 2022-12-11 13:39:20.079723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac8b8ff6849d'
down_revision = '4b68d8d52ad1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE INDEX idx_authors_metadata_author_id ON authors_metadata USING hash(author_id);
""")


def downgrade():
    op.execute("""
DROP INDEX idx_authors_metadata_author_id;
""")
